#!/usr/bin/env python3
"""
Test if OpenAI API key works
"""

import os
import sys

def test_api_key():
    """Test OpenAI API key"""
    
    # Check if key is set
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No API key found in environment variable OPENAI_API_KEY")
        print("\nTo set it:")
        print("  PowerShell: $env:OPENAI_API_KEY='your-key-here'")
        print("  Bash: export OPENAI_API_KEY='your-key-here'")
        return False
    
    print(f"✓ API key found (starts with: {api_key[:10]}...)")
    
    # Test the key
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        print("\n⏳ Testing API key with a simple request...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API key works!'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API key works! Response: {result}")
        return True
        
    except ImportError:
        print("❌ openai package not installed")
        print("   Run: pip install openai")
        return False
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)
