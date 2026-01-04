"""Quick start script for backend"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Plagiarism Checker Backend")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔧 CORS enabled for: http://localhost:3000")
    
    uvicorn.run(
        "app.main:app",  # Import string for reload
        host="0.0.0.0",
        port=8000,
        reload=True
    )
