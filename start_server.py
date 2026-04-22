#!/usr/bin/env python
"""
Startup script for Railway deployment.
Runs migrations then starts gunicorn.
"""
import os
import sys
import subprocess
import django

# Setup Django before running migrations
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthlink.settings')

def main():
    """Run migrations then start gunicorn"""
    
    try:
        print("=" * 70, flush=True)
        print("Starting HealthLink Django Application", flush=True)
        print("=" * 70, flush=True)
        print("", flush=True)
        
        sys.stdout.flush()
        sys.stderr.flush()
        
        print("Step 1: Initializing Django...", flush=True)
        django.setup()
        print("Django initialized successfully!", flush=True)
        print("", flush=True)
        
        sys.stdout.flush()
        
        print("Step 2: Running Database Migrations...", flush=True)
        print("=" * 70, flush=True)
        sys.stdout.flush()
        
        # Run migrations
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput", "--verbosity", "2"],
            text=True
        )
        
        sys.stdout.flush()
        sys.stderr.flush()
        
        print("=" * 70, flush=True)
        
        if result.returncode != 0:
            print(f"[ERROR] Migrations failed with return code {result.returncode}", flush=True)
            sys.stdout.flush()
            sys.exit(1)
        
        print("Migrations completed successfully!", flush=True)
        print("", flush=True)
        sys.stdout.flush()
        
        print("Step 3: Starting Gunicorn Server...", flush=True)
        print("=" * 70, flush=True)
        print("", flush=True)
        sys.stdout.flush()
        
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
        
    except Exception as e:
        print(f"[FATAL] Startup failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    main()

