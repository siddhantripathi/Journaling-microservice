import subprocess
import sys
import os
import signal
import time
from threading import Thread

def run_backend():
    # Activate virtual environment and run Flask
    if sys.platform == 'win32':
        venv_python = os.path.join('backend', 'venv', 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join('backend', 'venv', 'bin', 'python')
    
    # Load environment variables from .env
    env = os.environ.copy()
    if os.path.exists(os.path.join('backend', '.env')):
        with open(os.path.join('backend', '.env')) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env[key] = value

    backend_process = subprocess.Popen(
        [venv_python, os.path.join('backend', 'app.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=env
    )
    return backend_process

def run_frontend():
    try:
        # Use full Flutter path
        flutter_cmd = 'C:/flutter_windows_3.29.0-stable/flutter/bin/flutter.bat'  # From your package_config.json
        frontend_path = os.path.join(os.getcwd(), 'frontend')
        
        # Enable web support
        subprocess.run(
            [flutter_cmd, 'config', '--enable-web'],
            check=True,
            capture_output=True
        )
        
        # Ensure dependencies are up to date
        subprocess.run(
            [flutter_cmd, 'pub', 'get'],
            cwd=frontend_path,
            check=True,
            capture_output=True
        )
        
        # Build and run web
        frontend_process = subprocess.Popen(
            [flutter_cmd, 'run', '-d', 'chrome'],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Give Flutter time to start
        time.sleep(5)
        
        if frontend_process.poll() is not None:
            raise Exception("Flutter process terminated unexpectedly")
            
        return frontend_process
        
    except subprocess.CalledProcessError as e:
        print(f"\nERROR running Flutter command: {e.stderr}")
        raise
    except Exception as e:
        print(f"\nERROR starting frontend: {str(e)}")
        raise

def stream_output(process, prefix):
    for line in process.stdout:
        print(f"[{prefix}] {line.strip()}")
    for line in process.stderr:
        print(f"[{prefix} ERROR] {line.strip()}")

def main():
    print("Starting services...")
    processes = []
    
    try:
        # Start backend
        backend_process = run_backend()
        processes.append(('backend', backend_process))
        
        backend_thread = Thread(target=stream_output, args=(backend_process, 'BACKEND'))
        backend_thread.daemon = True
        backend_thread.start()
        
        # Wait for backend to initialize
        time.sleep(2)
        
        # Start frontend
        frontend_process = run_frontend()
        processes.append(('frontend', frontend_process))
        
        frontend_thread = Thread(target=stream_output, args=(frontend_process, 'FRONTEND'))
        frontend_thread.daemon = True
        frontend_thread.start()
        
        print("Services started! Press Ctrl+C to stop...")
        
        while True:
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    raise Exception(f"{name} process terminated unexpectedly")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down services...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Cleanup processes
        for _, process in processes:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
        sys.exit(1)

if __name__ == "__main__":
    main() 