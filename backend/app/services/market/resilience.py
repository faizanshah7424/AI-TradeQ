import asyncio
import time
import random
import logging
from enum import Enum
from typing import Callable, TypeVar, Any, Optional
from app.services.market.base import (
    MarketDataException,
    ProviderConnectionException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderResponseException,
    AssetNotFoundException,
)

logger = logging.getLogger("market.resilience")

T = TypeVar("T")

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    """
    Circuit breaker preventing cascading outages when external providers experience downtime.
    """
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_seconds: float = 30.0,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.recovery_timeout_seconds:
                logger.info("Circuit breaker '%s' transitioning OPEN -> HALF_OPEN", self.name)
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        if self.state != CircuitState.CLOSED:
            logger.info("Circuit breaker '%s' recovered -> CLOSED", self.name)
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def record_failure(self):
        self.failure_count += 1
        now = time.time()
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.warning("Circuit breaker '%s' tripped -> OPEN (failures=%d)", self.name, self.failure_count)
            self.state = CircuitState.OPEN
            self.last_state_change = now

class ResilienceManager:
    """
    Executes provider calls with retries, exponential backoff, jitter, and circuit breaking.
    """
    def __init__(self):
        self._circuit_breakers = {}

    def get_circuit_breaker(self, provider_name: str) -> CircuitBreaker:
        if provider_name not in self._circuit_breakers:
            self._circuit_breakers[provider_name] = CircuitBreaker(name=provider_name)
        return self._circuit_breakers[provider_name]

    async def execute_with_resilience(
        self,
        provider_name: str,
        operation: Callable[[], Any],
        max_retries: int = 3,
        base_backoff_seconds: float = 0.5,
    ) -> Any:
        breaker = self.get_circuit_breaker(provider_name)

        if not breaker.can_execute():
            raise MarketDataException(
                f"Provider '{provider_name}' is currently unavailable (Circuit Breaker OPEN).",
                provider=provider_name,
                status_code=503,
            )

        attempt = 0
        while attempt < max_retries:
            attempt += 1
            try:
                result = await operation()
                breaker.record_success()
                return result

            except AssetNotFoundException:
                # 404 is a permanent client domain error; do not retry or trip breaker
                raise

            except ProviderRateLimitException as e:
                breaker.record_failure()
                delay = e.retry_after_seconds or (base_backoff_seconds * (2 ** (attempt - 1)) + random.uniform(0.1, 0.5))
                logger.warning(
                    "Provider '%s' rate limited (attempt %d/%d). Backing off for %.2fs",
                    provider_name, attempt, max_retries, delay
                )
                if attempt >= max_retries:
                    raise
                await asyncio.sleep(delay)

            except (ProviderConnectionException, ProviderTimeoutException, ProviderResponseException) as e:
                breaker.record_failure()
                delay = base_backoff_seconds * (2 ** (attempt - 1)) + random.uniform(0.1, 0.4)
                logger.warning(
                    "Provider '%s' transient error (attempt %d/%d): %s. Retrying in %.2fs",
                    provider_name, attempt, max_retries, str(e), delay
                )
                if attempt >= max_retries:
                    raise
                await asyncio.sleep(delay)

            except Exception as e:
                breaker.record_failure()
                logger.error("Unexpected provider '%s' execution error: %s", provider_name, str(e))
                raise MarketDataException(f"Unexpected error executing provider '{provider_name}': {str(e)}", provider=provider_name)

resilience_manager = ResilienceManager()
