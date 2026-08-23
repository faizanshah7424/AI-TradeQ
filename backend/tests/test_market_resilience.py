import pytest
from app.services.market.resilience import CircuitBreaker, CircuitState, resilience_manager
from app.services.market.base import ProviderTimeoutException, MarketDataException

def test_circuit_breaker_state_transitions():
    cb = CircuitBreaker(name="test_provider", failure_threshold=3, recovery_timeout_seconds=0.1)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # Record 3 failures
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Record success resets
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

@pytest.mark.asyncio
async def test_resilience_manager_circuit_break():
    breaker = resilience_manager.get_circuit_breaker("failing_provider")
    breaker.state = CircuitState.OPEN
    breaker.last_state_change = 999999999999.0  # Far in the future so timeout hasn't elapsed

    with pytest.raises(MarketDataException) as exc_info:
        await resilience_manager.execute_with_resilience(
            "failing_provider",
            lambda: None,
        )
    assert "Circuit Breaker OPEN" in str(exc_info.value)
    breaker.state = CircuitState.CLOSED
