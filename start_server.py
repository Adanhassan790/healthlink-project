#!/usr/bin/env python
"""
Startup script for Railway deployment.
Runs migrations then starts gunicorn.
"""
import os
import sys
import subprocess

def main():
    """Run migrations then start gunicorn"""
    
    print("=" * 70)
    print("Starting HealthLink Django Application")
    print("=" * 70)
    print("")
    
    print("Step 1: Running Database Migrations...")
    print("=" * 70)
    
    # Run migrations
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        text=True
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Migrations failed with return code {result.returncode}")
        sys.exit(1)
    
    print("=" * 70)
    print("Migrations completed successfully!")
    print("")
    
    print("Step 2: Starting Gunicorn Server...")
    print("=" * 70)
    print("")
    
    # Start gunicorn - use os.execvp to replace this process
    os.execvp(
        "gunicorn",
        [
            "gunicorn",
            "--bind", "0.0.0.0:8000",
            "--workers", "4",
            "--worker-class", "sync",
            "--timeout", "120",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "healthlink.wsgi:application"
        ]
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Shutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] {str(e)}")
        sys.exit(1)
