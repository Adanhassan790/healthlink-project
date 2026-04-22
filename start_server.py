#!/usr/bin/env python
"""
Startup script for Railway deployment.
Runs migrations then starts gunicorn.
"""
import os
import sys
import subprocess

# Ensure unbuffered output
sys.stdout = open(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = open(sys.stderr.fileno(), 'w', buffering=1)

def run_migrations():
    """Run Django migrations"""
    print("=" * 60, flush=True)
    print("Running Django Migrations...", flush=True)
    print("=" * 60, flush=True)
    sys.stdout.flush()
    
    try:
        # Run migrations without cwd override (we're already in /app as WORKDIR)
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            capture_output=False,
            text=True
        )
        
        print("=" * 60, flush=True)
        
        if result.returncode != 0:
            print(f"[ERROR] Migrations failed with return code {result.returncode}", flush=True)
            sys.exit(1)
            
        print("Migrations completed successfully!", flush=True)
        print("=" * 60, flush=True)
        sys.stdout.flush()
        
    except Exception as e:
        print(f"[ERROR] Failed to run migrations: {str(e)}", flush=True)
        sys.stdout.flush()
        sys.exit(1)

def start_gunicorn():
    """Start gunicorn web server"""
    print("\n" + "=" * 60, flush=True)
    print("Starting Gunicorn...", flush=True)
    print("=" * 60 + "\n", flush=True)
    sys.stdout.flush()
    
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
    try:
        run_migrations()
        start_gunicorn()
    except Exception as e:
        print(f"[FATAL] Startup failed: {str(e)}", flush=True)
        sys.exit(1)
