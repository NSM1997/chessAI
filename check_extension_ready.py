#!/usr/bin/env python3
"""
Quick check to ensure the extension files are ready
"""
import os
import json

def check_file(path, description):
    """Check if a file exists and is not empty"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        if size > 0:
            print(f"  [OK] {description} ({size} bytes)")
            return True
        else:
            print(f"  [WARN] {description} is empty")
            return False
    else:
        print(f"  [MISSING] {description}")
        return False

def main():
    print("=" * 60)
    print("Chess AI Extension Readiness Check")
    print("=" * 60)
    
    base_dir = "frontend"
    
    # Check essential files
    files = [
        ("frontend/manifest.json", "Manifest"),
        ("frontend/popup/popup.html", "Popup HTML"),
        ("frontend/popup/popup.js", "Popup Script"),
        ("frontend/popup/popup.css", "Popup Styles"),
        ("frontend/content-scripts/content-script.js", "Content Script"),
        ("frontend/content-scripts/dom-extractors.js", "DOM Extractor"),
        ("frontend/background/background.js", "Background Script"),
        ("frontend/assets/icon16.png", "Icon 16x16"),
        ("frontend/assets/icon32.png", "Icon 32x32"),
        ("frontend/assets/icon48.png", "Icon 48x48"),
        ("frontend/assets/icon128.png", "Icon 128x128"),
    ]
    
    print("\nChecking Essential Files:")
    all_good = True
    for path, desc in files:
        if not check_file(path, desc):
            all_good = False
    
    # Check manifest.json content
    print("\nManifest Validation:")
    try:
        with open("frontend/manifest.json", "r") as f:
            manifest = json.load(f)
        print(f"  [OK] Extension name: {manifest.get('name')}")
        print(f"  [OK] Version: {manifest.get('version')}")
        print(f"  [OK] Manifest version: {manifest.get('manifest_version')}")
        
        # Check permissions
        permissions = manifest.get('permissions', [])
        print(f"  [OK] Permissions: {', '.join(permissions)}")
        
        # Check content scripts
        content_scripts = manifest.get('content_scripts', [])
        if content_scripts:
            print(f"  [OK] Content scripts configured: {len(content_scripts)} rule(s)")
        else:
            print(f"  [WARN] No content scripts found")
            all_good = False
            
    except Exception as e:
        print(f"  [ERROR] Failed to validate manifest: {e}")
        all_good = False
    
    # Check server status
    print("\nServer Status:")
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Server is running: {data.get('status')}")
        else:
            print(f"  [WARN] Server responded with status {response.status_code}")
    except Exception as e:
        print(f"  [ERROR] Server not accessible: {e}")
        all_good = False
    
    print("\n" + "=" * 60)
    if all_good:
        print("✓ Everything looks good! Ready to load extension.")
        print("\nNext steps:")
        print("1. Open Chrome: chrome://extensions/")
        print("2. Enable 'Developer mode'")
        print("3. Click 'Load unpacked'")
        print("4. Select: E:\\NCI\\Thesis\\explainable-chess-ai\\frontend")
        print("5. Test on: https://www.chess.com/puzzles")
    else:
        print("✗ Some issues detected. Please fix them before loading.")
    print("=" * 60)

if __name__ == "__main__":
    main()


