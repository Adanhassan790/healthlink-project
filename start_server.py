#!/usr/bin/env python
"""
Startup script for Railway deployment.
Runs migrations then starts gunicorn.
"""
import os
import sys
import subprocess

def run_migrations():
    """Run Django migrations"""
    print("=" * 60)
    print("Running Django Migrations...")
    print("=" * 60)
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            cwd="/app",
            capture_output=False
        )
        if result.returncode != 0:
            print(f"[ERROR] Migrations failed with return code {result.returncode}")
            sys.exit(1)
        print("=" * 60)
        print("Migrations completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Failed to run migrations: {str(e)}")
        sys.exit(1)

def start_gunicorn():
    """Start gunicorn web server"""
    print("\n" + "=" * 60)
    print("Starting Gunicorn...")
    print("=" * 60 + "\n")
    
    os.execvp(
        "gunicorn",
        [
            "gunicorn",
            "--bind", "0.0.0.0:8000",
            "--workers", "4",
            "--timeout", "120",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "healthlink.wsgi:application"
        ]
    )

if __name__ == "__main__":
    run_migrations()
    start_gunicorn()
