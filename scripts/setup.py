#!/usr/bin/env python3
"""
Setup script for Explainable Chess AI project
"""

import os
import sys
import subprocess
import platform
import requests
from pathlib import Path

def run_command(command, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    requirements = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "python-chess==1.999",
        "stockfish==3.28.0",
        "chess==1.10.0",
        "scikit-learn==1.3.0",
        "xgboost==2.0.0",
        "transformers==4.35.0",
        "torch==2.1.0",
        "pandas==2.1.0",
        "numpy==1.24.0",
        "python-multipart==0.0.6",
        "pydantic==2.4.0",
        "python-dotenv==1.0.0",
        "aiofiles==23.2.0",
        "httpx==0.25.0",
        "pytest==7.4.0",
        "pytest-asyncio==0.21.0"
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        result = run_command(f"pip install {package}")
        if result is None:
            print(f"Failed to install {package}")
            return False
    
    return True

def install_stockfish():
    """Install Stockfish chess engine"""
    print("Installing Stockfish...")
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        result = run_command("brew install stockfish")
    elif system == "linux":
        # Try different package managers
        if run_command("which apt-get", check=False):
            result = run_command("sudo apt-get update && sudo apt-get install -y stockfish")
        elif run_command("which yum", check=False):
            result = run_command("sudo yum install -y stockfish")
        else:
            print("Please install Stockfish manually for your Linux distribution")
            return False
    elif system == "windows":
        print("Please install Stockfish manually on Windows")
        print("Download from: https://stockfishchess.org/download/")
        return False
    
    # Verify installation
    stockfish_path = run_command("which stockfish", check=False)
    if stockfish_path:
        print(f"Stockfish installed at: {stockfish_path}")
        return True
    else:
        print("Stockfish installation verification failed")
        return False

def download_sample_data():
    """Download sample chess data for training"""
    print("Downloading sample training data...")
    
    data_dir = Path("backend/data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download a small Lichess database sample
    sample_url = "https://database.lichess.org/standard/lichess_db_standard_rated_2024-08.pgn.bz2"
    sample_file = data_dir / "lichess_sample.pgn.bz2"
    
    try:
        response = requests.get(sample_url, stream=True)
        response.raise_for_status()
        
        with open(sample_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded sample data to: {sample_file}")
        return True
        
    except Exception as e:
        print(f"Failed to download sample data: {e}")
        print("You can manually download PGN files from https://database.lichess.org/")
        return False

def create_env_file():
    """Create .env file with configuration"""
    print("Creating .env file...")
    
    env_content = """
# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=True

# Chess Engine Configuration
STOCKFISH_PATH=/usr/local/bin/stockfish
STOCKFISH_DEPTH=15
STOCKFISH_THREADS=2

# ML Configuration
MODEL_PATH=backend/models/saved_models
CACHE_SIZE=1000

# Data Configuration
DATA_PATH=backend/data
PGN_PATH=backend/data/raw
PROCESSED_PATH=backend/data/processed

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
"""
    
    with open('.env', 'w') as f:
        f.write(env_content.strip())
    
    print("Created .env file")
    return True

def setup_project_structure():
    """Create project directory structure"""
    print("Setting up project structure...")
    
    directories = [
        "backend/app/api",
        "backend/app/models", 
        "backend/app/services",
        "backend/app/core",
        "backend/data/raw",
        "backend/data/processed",
        "backend/models/saved_models",
        "backend/models/training_data",
        "frontend/popup",
        "frontend/content-scripts",
        "frontend/background",
        "frontend/components",
        "frontend/assets",
        "scripts",
        "tests",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if directory.startswith("backend/") and "/" in directory[8:]:
            init_file = Path(directory) / "__init__.py"
            init_file.touch(exist_ok=True)
    
    print("Project structure created")
    return True

def create_sample_icons():
    """Create placeholder icons for the extension"""
    print("Creating placeholder icons...")
    
    icons_dir = Path("frontend/assets")
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Create simple SVG icons as placeholders
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#667eea">
  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
</svg>'''
    
    # This is a placeholder - you should create proper icons
    for size in [16, 32, 48, 128]:
        icon_file = icons_dir / f"icon{size}.png"
        # In a real setup, you'd convert SVG to PNG at different sizes
        # For now, just create empty files as placeholders
        icon_file.touch(exist_ok=True)
    
    print("Placeholder icons created (replace with actual icons)")
    return True

def main():
    """Main setup function"""
    print("=== Explainable Chess AI Setup ===")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()}")
    print()
    
    # Setup steps
    steps = [
        ("Setting up project structure", setup_project_structure),
        ("Installing Python dependencies", install_python_dependencies),
        ("Installing Stockfish", install_stockfish),
        ("Creating configuration files", create_env_file),
        ("Creating placeholder icons", create_sample_icons),
        ("Downloading sample data", download_sample_data),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f">>> {step_name}...")
        try:
            success = step_func()
            if success:
                print(f"✓ {step_name} completed")
            else:
                print(f"✗ {step_name} failed")
                failed_steps.append(step_name)
        except Exception as e:
            print(f"✗ {step_name} failed with error: {e}")
            failed_steps.append(step_name)
        print()
    
    # Summary
    print("=== Setup Summary ===")
    if failed_steps:
        print("⚠️  Setup completed with some failures:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease address the failed steps manually.")
    else:
        print("✅ Setup completed successfully!")
    
    print("\nNext steps:")
    print("1. Start the backend server: cd backend && python -m app.main")
    print("2. Load the Chrome extension from the frontend/ directory")
    print("3. Visit chess.com or lichess.org to test the extension")
    print("\nFor development:")
    print("- Backend API docs: http://localhost:8000/docs")
    print("- Modify settings in .env file")
    print("- Add your own chess data to backend/data/raw/")

if __name__ == "__main__":
    main()
