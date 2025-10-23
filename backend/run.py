#!/usr/bin/env python3
"""
Application launcher script
"""
import uvicorn
import sys

if __name__ == "__main__":
    print("=" * 60)
    print("Credit Card Statement Parser API")
    print("=" * 60)
    print("\nStarting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/v1/health")
    print("\nPress CTRL+C to stop\n")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
