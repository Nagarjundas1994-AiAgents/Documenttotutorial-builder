#!/usr/bin/env python3
"""
Test Google and XAI API keys
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_google_api():
    """Test Google Gemini API"""
    print("🔍 Testing Google Gemini API...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == "your-google-gemini-api-key":
        print("❌ Google API key not configured")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[{"role": "user", "content": "Hello, this is a test. Please respond with 'Google API working!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Google API working: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Google API failed: {e}")
        return False

def test_xai_api():
    """Test XAI Grok API"""
    print("\n🔍 Testing XAI Grok API...")
    
    api_key = os.getenv('XAI_API_KEY')
    if not api_key or api_key == "your-xai-api-key":
        print("❌ XAI API key not configured")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        
        response = client.chat.completions.create(
            model="grok-2-1212",
            messages=[{"role": "user", "content": "Hello, this is a test. Please respond with 'XAI API working!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ XAI API working: {result}")
        return True
        
    except Exception as e:
        print(f"❌ XAI API failed: {e}")
        return False

def test_deepseek_api():
    """Test DeepSeek API"""
    print("\n🔍 Testing DeepSeek API...")
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key or api_key == "your-deepseek-api-key":
        print("❌ DeepSeek API key not configured")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello, this is a test. Please respond with 'DeepSeek API working!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ DeepSeek API working: {result}")
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek API failed: {e}")
        return False

def main():
    """Test all APIs"""
    print("🚀 Testing API Keys")
    print("=" * 40)
    
    results = []
    results.append(("Google Gemini", test_google_api()))
    results.append(("XAI Grok", test_xai_api()))
    results.append(("DeepSeek", test_deepseek_api()))
    
    print("\n" + "=" * 40)
    print("📊 API Test Results:")
    
    working_apis = []
    for name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {name}: {'Working' if status else 'Failed'}")
        if status:
            working_apis.append(name)
    
    if working_apis:
        print(f"\n🎉 {len(working_apis)} API(s) working: {', '.join(working_apis)}")
        print("Your app is ready to generate tutorials!")
    else:
        print("\n⚠️  No APIs working. Please check your .env file and API keys.")

if __name__ == "__main__":
    main()