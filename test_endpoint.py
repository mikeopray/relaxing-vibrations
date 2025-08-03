#!/usr/bin/env python3
"""
Test script for the RunPod FFmpeg endpoint
"""

import requests
import json
import time
import sys

def test_endpoint(endpoint_url, api_key, video_url, audio_url):
    """Test the RunPod endpoint with sample files"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "video_url": video_url,
            "audio_url": audio_url,
            "volume": 0.7,
            "output_filename": "test_output.mp4"
        }
    }
    
    print(f"Testing endpoint: {endpoint_url}")
    print(f"Video URL: {video_url}")
    print(f"Audio URL: {audio_url}")
    print("-" * 50)
    
    try:
        # Submit job
        response = requests.post(endpoint_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        job_id = result.get("id")
        
        print(f"Job submitted successfully!")
        print(f"Job ID: {job_id}")
        print(f"Status: {result.get('status', 'Unknown')}")
        
        if result.get("status") == "COMPLETED":
            print("Job completed immediately!")
            print(json.dumps(result.get("output", {}), indent=2))
            return True
        
        # Poll for completion
        status_url = f"{endpoint_url.replace('/run', '')}/{job_id}"
        
        print("\nPolling for completion...")
        max_attempts = 60  # 10 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(10)  # Wait 10 seconds between polls
            attempt += 1
            
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            
            status_result = status_response.json()
            status = status_result.get("status", "Unknown")
            
            print(f"Attempt {attempt}: Status = {status}")
            
            if status == "COMPLETED":
                print("\n✅ Job completed successfully!")
                output = status_result.get("output", {})
                print(json.dumps(output, indent=2))
                return True
                
            elif status == "FAILED":
                print("\n❌ Job failed!")
                error = status_result.get("error", "Unknown error")
                print(f"Error: {error}")
                return False
                
            elif status in ["IN_PROGRESS", "IN_QUEUE"]:
                continue
            else:
                print(f"\n⚠️ Unknown status: {status}")
                
        print("\n⏰ Job timed out after 10 minutes")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    
    # Default test URLs (replace with your own)
    DEFAULT_VIDEO = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    DEFAULT_AUDIO = "https://www.soundjay.com/misc/sounds/magic-chime-02.mp3"
    
    print("RunPod FFmpeg Endpoint Tester")
    print("=" * 40)
    
    # Get user input
    endpoint_url = input("Enter your RunPod endpoint URL (with /run): ").strip()
    if not endpoint_url:
        print("❌ Endpoint URL is required!")
        sys.exit(1)
    
    api_key = input("Enter your RunPod API key: ").strip()
    if not api_key:
        print("❌ API key is required!")
        sys.exit(1)
    
    video_url = input(f"Enter video URL (or press Enter for default): ").strip()
    if not video_url:
        video_url = DEFAULT_VIDEO
    
    audio_url = input(f"Enter audio URL (or press Enter for default): ").strip()
    if not audio_url:
        audio_url = DEFAULT_AUDIO
    
    print("\n" + "=" * 50)
    
    # Run test
    success = test_endpoint(endpoint_url, api_key, video_url, audio_url)
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("Your endpoint is working correctly.")
    else:
        print("\n💥 Test failed!")
        print("Check the logs above for error details.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()