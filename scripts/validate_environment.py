#!/usr/bin/env python3
"""
AI TradeQ — Development Environment Validation Script
Standardized verification tool for developer workstation environments.
Checks system requirements, installed runtime versions, required tools, and port availability.
"""

import sys
import subprocess
import socket
import shutil
import re
import platform

# ANSI Color Codes for Terminal Output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  AI TradeQ — {title}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}\n")

def check_command(cmd: str) -> bool:
    """Check if a CLI executable is available in PATH."""
    return shutil.which(cmd) is not None

def run_cmd(args: list[str]) -> tuple[bool, str]:
    """Execute command and return success status + output string."""
    try:
        res = subprocess.run(args, capture_output=True, text=True, timeout=10)
        output = (res.stdout + res.stderr).strip()
        return res.returncode == 0, output
    except Exception as e:
        return False, str(e)

def check_python_version() -> tuple[bool, str]:
    """Validate Python version requirement (Python 3.12.x, 3.12 <= version < 3.13)."""
    major, minor, micro = sys.version_info[:3]
    version_str = f"{major}.{minor}.{micro}"
    
    if major == 3 and minor == 12:
        return True, f"Python {version_str} (Compliant with 3.12.x specification)"
    elif major == 3 and minor >= 13:
        return False, f"Python {version_str} (INCOMPATIBLE: Python {major}.{minor} has known package compatibility issues. Required: Python 3.12.x)"
    else:
        return False, f"Python {version_str} (INCOMPATIBLE: Required Python 3.12.x, found {version_str})"

def check_node_version() -> tuple[bool, str]:
    """Validate Node.js version requirement (Node 22 LTS)."""
    if not check_command("node"):
        return False, "Node.js is not installed or not found in PATH."
    
    ok, output = run_cmd(["node", "--version"])
    if not ok:
        return False, f"Failed to execute node: {output}"
    
    match = re.search(r"v?(\d+)\.(\d+)\.(\d+)", output)
    if not match:
        return False, f"Unable to parse Node.js version from output: {output}"
    
    major = int(match.group(1))
    if major >= 22:
        return True, f"Node.js {match.group(0)} (Compliant with Node.js 22 LTS specification)"
    else:
        return False, f"Node.js {match.group(0)} (INCOMPATIBLE: Minimum supported Node.js version is 22 LTS)"

def check_pnpm() -> tuple[bool, str]:
    """Validate pnpm package manager."""
    if not check_command("pnpm"):
        return False, "pnpm is not installed. Install via 'npm install -g pnpm' or 'corepack enable'."
    
    ok, output = run_cmd(["pnpm", "--version"])
    if ok:
        return True, f"pnpm version {output}"
    return False, f"Failed to check pnpm version: {output}"

def check_git() -> tuple[bool, str]:
    """Validate Git installation."""
    if not check_command("git"):
        return False, "Git is not installed or not found in PATH."
    
    ok, output = run_cmd(["git", "--version"])
    if ok:
        return True, f"{output}"
    return False, f"Failed to check Git version: {output}"

def check_docker() -> tuple[bool, str]:
    """Validate Docker Desktop installation and engine status."""
    if not check_command("docker"):
        return False, "Docker CLI is not installed or not found in PATH."
    
    ok_ver, ver_output = run_cmd(["docker", "--version"])
    if not ok_ver:
        return False, f"Failed to check Docker CLI: {ver_output}"
    
    ok_info, info_output = run_cmd(["docker", "info"])
    if ok_info:
        return True, f"{ver_output} (Daemon is running and healthy)"
    else:
        return True, f"{ver_output} (WARNING: Docker installed, but daemon is not running or accessible)"

def check_port_available(port: int, service_name: str) -> tuple[bool, str]:
    """Check if a local TCP port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.bind(("127.0.0.1", port))
            return True, f"Port {port} ({service_name}) is AVAILABLE"
        except socket.error:
            return False, f"Port {port} ({service_name}) is OCCUPIED or IN USE"

def main():
    print_header("Development Environment Compliance Validation")
    print(f"Operating System : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Execution Python : {sys.executable}\n")

    results = []

    # 1. Python Version
    py_ok, py_msg = check_python_version()
    results.append(("Python 3.12 Standard", py_ok, py_msg))

    # 2. Node.js Version
    node_ok, node_msg = check_node_version()
    results.append(("Node.js 22 LTS", node_ok, node_msg))

    # 3. Package Manager (pnpm)
    pnpm_ok, pnpm_msg = check_pnpm()
    results.append(("pnpm Package Manager", pnpm_ok, pnpm_msg))

    # 4. Git
    git_ok, git_msg = check_git()
    results.append(("Git Source Control", git_ok, git_msg))

    # 5. Docker Runtime
    docker_ok, docker_msg = check_docker()
    results.append(("Docker Container Runtime", docker_ok, docker_msg))

    # 6. Required Development Ports
    ports_to_check = [
        (8000, "Backend FastAPI Server"),
        (3000, "Frontend Next.js Application"),
        (5432, "PostgreSQL Database"),
        (6379, "Redis Cache Server"),
    ]

    for port, service in ports_to_check:
        port_ok, port_msg = check_port_available(port, service)
        results.append((f"Port {port} ({service})", port_ok, port_msg))

    # Render Summary Report Table
    print(f"{BOLD}{'COMPONENT / CHECK':<35} | {'STATUS':<10} | {'DETAILS'}{RESET}")
    print("-" * 80)

    all_passed = True
    for item, status, detail in results:
        if status:
            status_str = f"{GREEN}[PASS]{RESET}"
        else:
            status_str = f"{RED}[FAIL]{RESET}"
            all_passed = False
        print(f"{item:<35} | {status_str:<19} | {detail}")

    print("-" * 80)
    if all_passed:
        print(f"\n{BOLD}{GREEN}✓ SUCCESS: All development environment requirements passed successfully!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{BOLD}{RED}✗ FAILED: One or more environment checks failed. Please address the issues listed above.{RESET}")
        print(f"{YELLOW}Hint: To switch Python version to 3.12, use 'py -3.12' on Windows or 'pyenv local 3.12' on Unix.{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
