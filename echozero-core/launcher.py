#!/usr/bin/env python3
"""
EchoZero Standalone Desktop Launcher

Launches both the FastAPI backend and Streamlit UI in a single application.
Works on Windows, macOS, and Linux.

Usage:
    python launcher.py

Or create executable:
    pyinstaller launcher.spec
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading
import signal
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 8501
BACKEND_HOST = "127.0.0.1"
FRONTEND_HOST = "127.0.0.1"


class EchoZeroApp:
    """Standalone EchoZero application manager"""

    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True

        # Get app directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_dir = Path(sys._MEIPASS)
        else:
            # Running as script
            self.app_dir = Path(__file__).parent

        logger.info(f"App directory: {self.app_dir}")

    def start_backend(self):
        """Start FastAPI backend server"""
        logger.info(f"Starting backend on {BACKEND_HOST}:{BACKEND_PORT}")

        try:
            self.backend_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "app:app",
                    "--host", BACKEND_HOST,
                    "--port", str(BACKEND_PORT),
                    "--log-level", "warning"
                ],
                cwd=str(self.app_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("✓ Backend started")
            return True
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            return False

    def start_frontend(self):
        """Start Streamlit frontend"""
        logger.info(f"Starting frontend on {FRONTEND_HOST}:{FRONTEND_PORT}")

        try:
            self.frontend_process = subprocess.Popen(
                [
                    sys.executable, "-m", "streamlit", "run",
                    "streamlit_app.py",
                    "--server.port", str(FRONTEND_PORT),
                    "--server.address", FRONTEND_HOST,
                    "--server.headless", "true",
                    "--browser.gatherUsageStats", "false"
                ],
                cwd=str(self.app_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("✓ Frontend started")
            return True
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return False

    def open_browser(self):
        """Open browser to Streamlit UI"""
        url = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"
        logger.info(f"Opening browser to {url}")
        time.sleep(3)  # Wait for Streamlit to fully start

        try:
            webbrowser.open(url)
            logger.info("✓ Browser opened")
        except Exception as e:
            logger.warning(f"Could not open browser automatically: {e}")
            logger.info(f"Please open {url} manually")

    def stop(self):
        """Stop all processes"""
        logger.info("Shutting down EchoZero...")
        self.running = False

        if self.frontend_process:
            logger.info("Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()

        if self.backend_process:
            logger.info("Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()

        logger.info("✓ EchoZero stopped")

    def run(self):
        """Main run loop"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: self.stop())
        signal.signal(signal.SIGTERM, lambda s, f: self.stop())

        logger.info("=" * 60)
        logger.info("🌀 EchoZero Resonant AI System")
        logger.info("=" * 60)

        # Start backend
        if not self.start_backend():
            logger.error("Failed to start backend. Exiting.")
            return 1

        time.sleep(2)  # Let backend initialize

        # Start frontend
        if not self.start_frontend():
            logger.error("Failed to start frontend. Exiting.")
            self.stop()
            return 1

        # Open browser in separate thread
        browser_thread = threading.Thread(target=self.open_browser, daemon=True)
        browser_thread.start()

        logger.info("=" * 60)
        logger.info("✓ EchoZero is running!")
        logger.info(f"   Frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
        logger.info(f"   Backend API: http://{BACKEND_HOST}:{BACKEND_PORT}")
        logger.info("   Press Ctrl+C to stop")
        logger.info("=" * 60)

        # Monitor processes
        try:
            while self.running:
                time.sleep(1)

                # Check if processes are still alive
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("Backend process died unexpectedly")
                    break

                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.error("Frontend process died unexpectedly")
                    break

        except KeyboardInterrupt:
            logger.info("\nReceived interrupt signal")

        finally:
            self.stop()

        return 0


def main():
    """Entry point"""
    app = EchoZeroApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
