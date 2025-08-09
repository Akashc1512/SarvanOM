#!/usr/bin/env python3
"""
Development environment manager for Universal Knowledge Hub.
"""

import asyncio
import subprocess
import sys
import time
import threading
import signal
import os
from typing import Optional, List
import httpx


class DevelopmentManager:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True

    def setup_environment(self) -> bool:
        """Set up the development environment."""
        print("🚀 Setting up Universal Knowledge Hub development environment...")

        # Check if .env exists, create from template if not
        env_file = Path(".env")
        env_template = Path("env.template")

        if not env_file.exists():
            if env_template.exists():
                print("📝 Creating .env file from template...")
                with open(env_template, "r") as f:
                    template_content = f.read()

                with open(env_file, "w") as f:
                    f.write(template_content)

                print("✅ Created .env file")
                print("⚠️  Please update the following API keys in .env:")
                print("   - OPENAI_API_KEY")
                print("   - ANTHROPIC_API_KEY")
                print("   - PINECONE_API_KEY (optional)")
            else:
                print("❌ env.template not found")
                return False

        return True

    def install_python_dependencies(self) -> bool:
        """Install Python dependencies."""
        print("\n📦 Installing Python dependencies...")

        try:
            # Create virtual environment if it doesn't exist
            venv_path = Path(".venv")
            if not venv_path.exists():
                print("Creating virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)

            # Install requirements
            if os.name == "nt":  # Windows
                pip_path = ".venv/Scripts/pip.exe"
            else:  # Unix/Linux
                pip_path = ".venv/bin/pip"

            subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
            print("✅ Python dependencies installed")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing Python dependencies: {e}")
            return False

    def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies."""
        print("\n📦 Installing Node.js dependencies...")

        frontend_path = Path("frontend")
        if not frontend_path.exists():
            print("❌ Frontend directory not found")
            return False

        try:
            # Clean install
            subprocess.run(
                ["npm", "cache", "clean", "--force"], cwd=frontend_path, check=True
            )
            subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
            print("✅ Node.js dependencies installed")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing Node.js dependencies: {e}")
            return False

    def start_backend(self) -> Optional[subprocess.Popen]:
        """Start the backend server."""
        print("\n🔧 Starting backend server...")

        try:
            if os.name == "nt":  # Windows
                python_path = ".venv/Scripts/python.exe"
            else:  # Unix/Linux
                python_path = ".venv/bin/python"

            # Start the backend
            process = subprocess.Popen(
                [
                    python_path,
                    "-m",
                    "uvicorn",
                    "api.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8002",
                    "--reload",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait a moment to see if it starts successfully
            time.sleep(3)
            if process.poll() is None:
                print("✅ Backend server started on http://localhost:8002")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Backend failed to start: {stderr}")
                return None

        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return None

    def start_frontend(self) -> Optional[subprocess.Popen]:
        """Start the frontend development server."""
        print("\n🎨 Starting frontend development server...")

        try:
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="frontend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait a moment to see if it starts successfully
            time.sleep(5)
            if process.poll() is None:
                print("✅ Frontend server started on http://localhost:3000")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Frontend failed to start: {stderr}")
                return None

        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return None

    async def check_health(self) -> None:
        """Check the health of running services."""
        print("\n🏥 Checking service health...")

        # Check backend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8002/health", timeout=5.0)
                if response.status_code == 200:
                    print("✅ Backend is healthy")
                else:
                    print("⚠️  Backend health check failed")
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")

        # Check frontend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:3000", timeout=5.0)
                if response.status_code == 200:
                    print("✅ Frontend is healthy")
                else:
                    print("⚠️  Frontend health check failed")
        except Exception as e:
            print(f"❌ Frontend health check failed: {e}")

    def monitor_processes(self) -> None:
        """Monitor running processes and restart if needed."""
        while self.running:
            for i, process in enumerate(self.processes):
                if process.poll() is not None:
                    print(f"⚠️  Process {i} stopped unexpectedly")
                    # Restart logic could be added here
            time.sleep(5)

    def cleanup(self) -> None:
        """Clean up running processes."""
        print("\n🛑 Shutting down services...")
        self.running = False

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error stopping process: {e}")

    async def run(self) -> None:
        """Main run method."""
        try:
            # Setup
            if not self.setup_environment():
                return

            if not self.install_python_dependencies():
                return

            if not self.install_node_dependencies():
                return

            # Start services
            backend_process = self.start_backend()
            if backend_process:
                self.processes.append(backend_process)

            frontend_process = self.start_frontend()
            if frontend_process:
                self.processes.append(frontend_process)

            if not self.processes:
                print("❌ Failed to start any services")
                return

            # Check health
            await asyncio.sleep(2)
            await self.check_health()

            # Start monitoring in background
            monitor_thread = threading.Thread(
                target=self.monitor_processes, daemon=True
            )
            monitor_thread.start()

            print("\n" + "=" * 60)
            print("🎉 Universal Knowledge Hub is running!")
            print("=" * 60)
            print("📱 Frontend: http://localhost:3000")
            print("🔧 Backend:  http://localhost:8002")
            print("📚 API Docs: http://localhost:8002/docs")
            print("\nPress Ctrl+C to stop all services")
            print("=" * 60)

            # Keep running
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            self.cleanup()


async def main():
    """Main function."""
    manager = DevelopmentManager()

    def signal_handler(signum, frame):
        print("\n🛑 Received signal to stop")
        manager.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await manager.run()


if __name__ == "__main__":
    asyncio.run(main())
