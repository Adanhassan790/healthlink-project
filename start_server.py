#!/usr/bin/env python
"""
Startup script for Railway deployment.
Runs migrations then starts gunicorn.
"""
import os
import sys
import subprocess
import django
from datetime import datetime

# Setup Django before running migrations
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthlink.settings')

def log_message(message):
    """Log message to stdout and file"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    full_message = f"[{timestamp}] {message}"
    print(full_message, flush=True)
    sys.stdout.flush()
    # Also write to file for debugging
    try:
        with open('/tmp/healthlink-startup.log', 'a') as f:
            f.write(full_message + '\n')
            f.flush()
    except:
        pass

def main():
    """Run migrations then start gunicorn"""
    
    log_message("=" * 70)
    log_message("STARTUP SCRIPT EXECUTION STARTED")
    log_message("=" * 70)
    log_message(f"Python: {sys.executable}")
    log_message(f"CWD: {os.getcwd()}")
    log_message(f"PID: {os.getpid()}")
    log_message("")
    
    try:
        log_message("Step 1: Initializing Django...")
        django.setup()
        log_message("✓ Django initialized successfully!")
        log_message("")
        
        log_message("Step 2: Running Database Migrations...")
        log_message("=" * 70)
        sys.stdout.flush()
        
        # Run migrations
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput", "--verbosity", "2"],
            text=True
        )
        
        sys.stdout.flush()
        sys.stderr.flush()
        
        log_message("=" * 70)
        
        if result.returncode != 0:
            log_message(f"✗ Migrations failed with return code {result.returncode}")
            sys.stdout.flush()
            sys.exit(1)
        
        log_message("✓ Migrations completed successfully!")
        log_message("")
        
        log_message("Step 3: Starting Gunicorn Server...")
        log_message("=" * 70)
        log_message("")
        sys.stdout.flush()
        
        # Start gunicorn - use os.execvp to replace this process
        log_message("Replacing process with gunicorn...")
        sys.stdout.flush()
        
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
        log_message(f"✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)

if __name__ == "__main__":
    log_message("Script __main__ block entered")
    main()


