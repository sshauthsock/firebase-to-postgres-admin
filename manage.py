#!/usr/bin/env python
import sys
import os
import subprocess
import signal
import time
from pathlib import Path


def find_process_on_port(port):
    try:
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    return int(parts[-1])
    except Exception:
        pass
    return None


def kill_process(pid):
    try:
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=False)
        else:
            os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        return False


def stop_server():
    print("Stopping server...")
    pid = find_process_on_port(8000)
    if pid:
        print(f"  Found process PID {pid}")
        if kill_process(pid):
            print("  Server stopped")
            time.sleep(1)
        else:
            print("  Failed to stop server")
    else:
        print("  No server running on port 8000")


def clean_cache():
    print("Cleaning Python cache...")
    cache_dirs = ['__pycache__', 'app/__pycache__']
    for cache_dir in cache_dirs:
        cache_path = Path(cache_dir)
        if cache_path.exists():
            import shutil
            shutil.rmtree(cache_path)
            print(f"  Removed {cache_dir}")


def start_server():
    stop_server()
    clean_cache()
    
    print("\nStarting server...")
    print("  Server will be available at: http://127.0.0.1:8000")
    print("  API docs: http://127.0.0.1:8000/docs")
    print("  Press Ctrl+C to stop\n")
    
    venv_python = Path('.venv/Scripts/python.exe' if sys.platform == 'win32' else '.venv/bin/python')
    if not venv_python.exists():
        python_cmd = sys.executable
    else:
        python_cmd = str(venv_python)
    
    try:
        subprocess.run([
            python_cmd,
            '-m', 'uvicorn',
            'app.main:app',
            '--reload',
            '--host', '127.0.0.1',
            '--port', '8000'
        ])
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        stop_server()


def restart_server():
    stop_server()
    time.sleep(2)
    start_server()


def show_status():
    pid = find_process_on_port(8000)
    if pid:
        print(f"Server is running (PID: {pid})")
        print("  URL: http://127.0.0.1:8000")
        print("  Docs: http://127.0.0.1:8000/docs")
    else:
        print("Server is not running")


def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py [start|stop|restart|status]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_server()
    elif command == 'stop':
        stop_server()
    elif command == 'restart':
        restart_server()
    elif command == 'status':
        show_status()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python manage.py [start|stop|restart|status]")
        sys.exit(1)


if __name__ == '__main__':
    main()

