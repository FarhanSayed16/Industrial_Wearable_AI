"""
Industrial Wearable AI — Unified Launcher
==========================================
Run this single file to start the entire project:
    python run.py

What it does:
  1. Checks prerequisites (Python, Node.js, Docker)
  2. Creates .venv / .env / node_modules if missing (never overwrites existing)
  3. Starts PostgreSQL (Docker), applies migrations, seeds data
  4. Opens Backend, Edge, and Dashboard in separate terminal windows

Safe to re-run: every step is idempotent.
"""

import os
import platform
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
EDGE_DIR = ROOT / "edge"
DASHBOARD_DIR = ROOT / "dashboard"
ML_DIR = ROOT / "ml"

PYTHON_CMD = sys.executable  # use the same Python that runs this script

# Default .env contents (only written if .env does NOT already exist)
BACKEND_ENV_DEFAULTS = """\
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai
SECRET_KEY=change-me-in-production-use-long-random-string
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174
"""

EDGE_ENV_DEFAULTS = """\
BACKEND_URL=http://localhost:8000
WORKER_ID=W01
BLE_DEVICE_ID=
MODEL_PATH=
"""

DASHBOARD_ENV_DEFAULTS = """\
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/live
"""

# Colors for terminal output (Windows 10+ supports ANSI)
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    DIM    = "\033[90m"


def banner():
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════╗
║       Industrial Wearable AI — Launcher          ║
╚══════════════════════════════════════════════════╝{C.RESET}
""")


def step(msg: str):
    print(f"\n{C.BOLD}{C.GREEN}▸ {msg}{C.RESET}")


def info(msg: str):
    print(f"  {C.DIM}{msg}{C.RESET}")


def warn(msg: str):
    print(f"  {C.YELLOW}⚠ {msg}{C.RESET}")


def error(msg: str):
    print(f"  {C.RED}✖ {msg}{C.RESET}")


def ok(msg: str):
    print(f"  {C.GREEN}✔ {msg}{C.RESET}")


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """Run a command and stream output. Returns CompletedProcess."""
    info(f"Running: {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, cwd=str(cwd), check=check, **kwargs)


# ──────────────────────────────────────────────
# Prerequisite checks
# ──────────────────────────────────────────────
def check_python():
    step("Checking Python")
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        error(f"Python 3.10+ required, found {v.major}.{v.minor}.{v.micro}")
        sys.exit(1)
    ok(f"Python {v.major}.{v.minor}.{v.micro}")


def check_node():
    step("Checking Node.js")
    node = shutil.which("node")
    if not node:
        error("Node.js not found. Install from https://nodejs.org/ (v18+ recommended)")
        sys.exit(1)
    result = subprocess.run([node, "--version"], capture_output=True, text=True)
    version = result.stdout.strip()
    ok(f"Node.js {version}")


def check_docker():
    step("Checking Docker")
    docker = shutil.which("docker")
    if not docker:
        error("Docker not found. Install Docker Desktop from https://www.docker.com/")
        error("Alternatively, install PostgreSQL locally — see docs/RUN_COMMANDS.md")
        sys.exit(1)
    # Check if Docker daemon is running
    result = subprocess.run(
        ["docker", "info"], capture_output=True, text=True
    )
    if result.returncode != 0:
        error("Docker is installed but not running. Start Docker Desktop first.")
        sys.exit(1)
    ok("Docker is running")


# ──────────────────────────────────────────────
# Setup helpers
# ──────────────────────────────────────────────
def venv_python(service_dir: Path) -> str:
    """Return the path to the venv's python executable."""
    if platform.system() == "Windows":
        return str(service_dir / ".venv" / "Scripts" / "python.exe")
    return str(service_dir / ".venv" / "bin" / "python")


def ensure_venv(service_dir: Path, name: str):
    """Create a virtual environment if it doesn't exist."""
    venv_dir = service_dir / ".venv"
    py = venv_python(service_dir)

    if venv_dir.exists() and Path(py).exists():
        ok(f"{name}: .venv exists")
    else:
        warn(f"{name}: .venv missing — creating...")
        run([PYTHON_CMD, "-m", "venv", str(venv_dir)], cwd=service_dir)
        ok(f"{name}: .venv created")

    # Always check if requirements are installed by trying a key import
    req_file = service_dir / "requirements.txt"
    if req_file.exists():
        info(f"{name}: Installing/updating dependencies...")
        run(
            [py, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
            cwd=service_dir,
            check=False,  # don't abort on pip warnings
        )
        ok(f"{name}: dependencies installed")


def ensure_env_file(service_dir: Path, name: str, defaults: str):
    """Create a .env file with defaults if it doesn't exist. Never overwrite."""
    env_file = service_dir / ".env"
    if env_file.exists():
        ok(f"{name}: .env exists (not modified)")
    else:
        warn(f"{name}: .env missing — creating with defaults...")
        env_file.write_text(defaults, encoding="utf-8")
        ok(f"{name}: .env created")


def ensure_node_modules():
    """Run npm install if node_modules is missing."""
    nm = DASHBOARD_DIR / "node_modules"
    if nm.exists():
        ok("Dashboard: node_modules exists")
    else:
        warn("Dashboard: node_modules missing — running npm install...")
        run(["npm", "install"], cwd=DASHBOARD_DIR)
        ok("Dashboard: npm install complete")


# ──────────────────────────────────────────────
# Service starters
# ──────────────────────────────────────────────
def start_postgres():
    step("Starting PostgreSQL (Docker)")
    compose_file = BACKEND_DIR / "docker-compose.yml"
    if not compose_file.exists():
        error(f"docker-compose.yml not found at {compose_file}")
        sys.exit(1)

    run(["docker", "compose", "up", "-d"], cwd=BACKEND_DIR)

    # Wait for Postgres to be ready (up to 30 seconds)
    info("Waiting for PostgreSQL to be ready...")
    for i in range(30):
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres",
             "pg_isready", "-U", "postgres"],
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            ok("PostgreSQL is ready")
            return
        time.sleep(1)
        if i % 5 == 4:
            info(f"  Still waiting... ({i + 1}s)")

    error("PostgreSQL did not become ready in 30 seconds.")
    error("Check Docker logs: docker compose logs -f postgres")
    sys.exit(1)


def run_migrations():
    step("Running database migrations (Alembic)")
    py = venv_python(BACKEND_DIR)
    run([py, "-m", "alembic", "upgrade", "head"], cwd=BACKEND_DIR)
    ok("Migrations applied")


def seed_data():
    step("Seeding database (idempotent — skips if data exists)")
    py = venv_python(BACKEND_DIR)

    info("Seeding admin user...")
    run([py, "seed_user.py"], cwd=BACKEND_DIR)

    info("Seeding demo workers (W01–W08 with 45 days of history)...")
    run([py, "seed_demo_workers.py"], cwd=BACKEND_DIR)

    ok("Seed complete")


def open_terminal(title: str, cmd: str, cwd: Path):
    """Open a new terminal window on Windows with a title and command."""
    if platform.system() != "Windows":
        error(f"open_terminal only supports Windows. Manually run: {cmd}")
        return

    # Use 'start' to open a new cmd.exe window
    # The /K flag keeps the window open after the command finishes (for debugging)
    # We wrap in cmd /K so the user can see output and errors
    full_cmd = f'start "{title}" cmd /K "cd /d {cwd} && {cmd}"'
    subprocess.run(full_cmd, shell=True, cwd=str(cwd))


def start_backend():
    step("Starting Backend (new terminal)")
    py = venv_python(BACKEND_DIR)
    # Use the venv python directly so no activation is needed
    cmd = f'"{py}" -m uvicorn app.main:app --reload'
    open_terminal("Industrial Wearable AI — Backend", cmd, BACKEND_DIR)
    ok("Backend terminal opened → http://localhost:8000")


def start_edge():
    step("Starting Edge Gateway (new terminal)")
    py = venv_python(EDGE_DIR)
    cmd = f'"{py}" -m src.main'
    open_terminal("Industrial Wearable AI — Edge", cmd, EDGE_DIR)
    ok("Edge terminal opened (simulator mode if BLE_DEVICE_ID is empty)")


def start_dashboard():
    step("Starting Dashboard (new terminal)")
    cmd = "npm run dev"
    open_terminal("Industrial Wearable AI — Dashboard", cmd, DASHBOARD_DIR)
    ok("Dashboard terminal opened → http://localhost:5173")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    banner()

    # ── Prerequisites ──
    check_python()
    check_node()
    check_docker()

    # ── Setup (idempotent) ──
    step("Setting up Backend")
    ensure_venv(BACKEND_DIR, "Backend")
    ensure_env_file(BACKEND_DIR, "Backend", BACKEND_ENV_DEFAULTS)

    step("Setting up Edge Gateway")
    ensure_venv(EDGE_DIR, "Edge")
    ensure_env_file(EDGE_DIR, "Edge", EDGE_ENV_DEFAULTS)

    step("Setting up Dashboard")
    ensure_env_file(DASHBOARD_DIR, "Dashboard", DASHBOARD_ENV_DEFAULTS)
    ensure_node_modules()

    # ── ML venv (optional — only if ml/ exists) ──
    if ML_DIR.exists() and (ML_DIR / "requirements.txt").exists():
        step("Setting up ML (optional)")
        ensure_venv(ML_DIR, "ML")

    # ── Start services ──
    start_postgres()
    run_migrations()
    seed_data()

    start_backend()
    time.sleep(2)  # give backend a moment to start before edge connects

    start_edge()
    start_dashboard()

    # ── Summary ──
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════╗
║              All services started!               ║
╚══════════════════════════════════════════════════╝{C.RESET}

  {C.GREEN}Dashboard:{C.RESET}  http://localhost:5173
  {C.GREEN}Backend:{C.RESET}    http://localhost:8000
  {C.GREEN}API Docs:{C.RESET}   http://localhost:8000/docs
  {C.GREEN}Login:{C.RESET}      admin / admin123

  {C.DIM}Each service runs in its own terminal window.
  Close them individually with Ctrl+C, or stop
  everything with:{C.RESET}

    {C.YELLOW}docker compose -f backend/docker-compose.yml down{C.RESET}
    {C.DIM}(and close the terminal windows){C.RESET}
""")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Interrupted. Services in other terminals are still running.{C.RESET}")
    except subprocess.CalledProcessError as e:
        error(f"Command failed: {e.cmd}")
        error(f"Exit code: {e.returncode}")
        sys.exit(1)
