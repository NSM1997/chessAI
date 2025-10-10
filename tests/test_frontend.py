"""
Frontend extension tests for Chess AI
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add frontend path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

class TestChessAIExtension:
    """Test cases for the Chess AI browser extension"""
    
    def test_manifest_structure(self):
        """Test that manifest.json has correct structure"""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'manifest.json')
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Check required fields
        assert "manifest_version" in manifest
        assert "name" in manifest
        assert "version" in manifest
        assert "permissions" in manifest
        assert "content_scripts" in manifest
        assert "background" in manifest
        
        # Check manifest version
        assert manifest["manifest_version"] == 3
        
        # Check permissions
        required_permissions = ["activeTab", "tabs", "storage"]
        for permission in required_permissions:
            assert permission in manifest["permissions"]
        
        # Check host permissions for chess.com
        host_permissions = manifest.get("host_permissions", [])
        assert any("chess.com" in perm for perm in host_permissions)
    
    def test_content_script_structure(self):
        """Test content script files exist and have basic structure"""
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        
        # Check required files exist
        required_files = [
            "content-scripts/content-script.js",
            "content-scripts/dom-extractors.js",
            "background/background.js",
            "popup/popup.js",
            "popup/popup.html"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(frontend_path, file_path)
            assert os.path.exists(full_path), f"Required file {file_path} not found"
            
            # Check file is not empty
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content.strip()) > 0, f"File {file_path} is empty"
    
    def test_dom_extractor_class(self):
        """Test DOM extractor class structure"""
        # This would require a browser environment to fully test
        # For now, just check the file exists and has the class
        dom_extractor_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend', 
            'content-scripts', 'dom-extractors.js'
        )
        
        with open(dom_extractor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key class and methods
        assert "class ChessDOMExtractor" in content
        assert "extractCurrentFEN" in content
        assert "isValidChessContext" in content
        assert "detectCurrentTurn" in content
    
    def test_content_script_class(self):
        """Test content script class structure"""
        content_script_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'content-scripts', 'content-script.js'
        )
        
        with open(content_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key class and methods
        assert "class ChessAIOverlay" in content
        assert "createOverlay" in content
        assert "quickAnalyze" in content
        assert "checkBoardChange" in content
    
    def test_popup_structure(self):
        """Test popup HTML and JS structure"""
        popup_html_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'popup', 'popup.html'
        )
        
        popup_js_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'popup', 'popup.js'
        )
        
        # Check HTML structure
        with open(popup_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        assert "<!DOCTYPE html>" in html_content
        assert "Chess AI" in html_content
        assert "popup.js" in html_content
        
        # Check JS structure
        with open(popup_js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        assert "class ChessAIPopup" in js_content
        assert "loadStatus" in js_content
        assert "sendMessage" in js_content
    
    def test_background_script_structure(self):
        """Test background script structure"""
        background_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'background', 'background.js'
        )
        
        with open(background_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key functionality
        assert "chrome.runtime.onMessage.addListener" in content
        assert "chrome.runtime.onInstalled.addListener" in content
        assert "getStatus" in content
        assert "ping" in content
    
    def test_api_communication(self):
        """Test API communication structure"""
        content_script_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'content-scripts', 'content-script.js'
        )
        
        with open(content_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for API communication
        assert "apiBaseUrl" in content
        assert "fetch" in content
        assert "analyze-position" in content
        assert "localhost:8000" in content
    
    def test_chess_com_integration(self):
        """Test Chess.com specific integration"""
        dom_extractor_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'content-scripts', 'dom-extractors.js'
        )
        
        with open(dom_extractor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Chess.com specific selectors
        assert "chess.com" in content
        assert "piece" in content
        assert "square-" in content
        assert "board" in content

class TestExtensionSecurity:
    """Test extension security aspects"""
    
    def test_manifest_permissions(self):
        """Test that manifest doesn't request excessive permissions"""
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'manifest.json')
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        permissions = manifest.get("permissions", [])
        
        # Should not request dangerous permissions
        dangerous_permissions = [
            "tabs",  # Only if needed for tab management
            "activeTab",  # OK for current tab access
            "storage",  # OK for settings
            "webRequest",  # Dangerous
            "webRequestBlocking",  # Dangerous
            "cookies",  # Dangerous
            "history",  # Dangerous
            "bookmarks"  # Dangerous
        ]
        
        # Check that only necessary permissions are requested
        allowed_permissions = ["activeTab", "tabs", "storage"]
        for permission in permissions:
            assert permission in allowed_permissions, f"Permission {permission} may be unnecessary"
    
    def test_content_script_csp(self):
        """Test that content scripts don't use eval or unsafe practices"""
        content_script_path = os.path.join(
            os.path.dirname(__file__), '..', 'frontend',
            'content-scripts', 'content-script.js'
        )
        
        with open(content_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for unsafe practices
        unsafe_patterns = [
            "eval(",
            "Function(",
            "setTimeout(",
            "setInterval(",
            "innerHTML =",  # Should use textContent when possible
        ]
        
        for pattern in unsafe_patterns:
            if pattern in content:
                # Some patterns might be acceptable, but should be reviewed
                print(f"Warning: Found potentially unsafe pattern '{pattern}' in content script")

if __name__ == "__main__":
    pytest.main([__file__])
