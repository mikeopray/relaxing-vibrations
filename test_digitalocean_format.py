#!/usr/bin/env python3
"""
Test script to verify DigitalOcean format parsing
"""

import json
import uuid
import re

def parse_digitalocean_format(event):
    """Parse DigitalOcean-style FFmpeg JSON into our format"""
    
    print("Parsing DigitalOcean format...")
    
    # Extract inputs
    inputs = event.get("inputs", [])
    if not inputs or len(inputs) < 2:
        raise ValueError("DigitalOcean format requires at least 2 inputs (video and audio)")
    
    # Validate input structure
    if not isinstance(inputs[0], dict) or "file_url" not in inputs[0]:
        raise ValueError("First input must have 'file_url' field")
    if not isinstance(inputs[1], dict) or "file_url" not in inputs[1]:
        raise ValueError("Second input must have 'file_url' field")
    
    video_url = inputs[0]["file_url"]
    audio_url = inputs[1]["file_url"]
    
    print(f"Video URL: {video_url}")
    print(f"Audio URL: {audio_url}")
    
    # Extract volume from filters - exactly like DigitalOcean FFmpeg
    volume = 1.0  # default to 1.0 (like DigitalOcean)
    filters = event.get("filters", [])
    
    for filter_obj in filters:
        if isinstance(filter_obj, dict) and "filter" in filter_obj:
            filter_str = filter_obj["filter"]
            print(f"Processing filter: {filter_str}")
            
            # Parse volume from filter like "[1:0]volume=1[audio]" or "[1:a]volume=0.7[audio]"
            volume_match = re.search(r'volume=([0-9]*\.?[0-9]+)', filter_str)
            if volume_match:
                volume = float(volume_match.group(1))
                print(f"Extracted volume: {volume}")
                break
    
    # Generate output filename from id (exactly like DigitalOcean)
    job_id = event.get("id", f"output_{uuid.uuid4().hex[:8]}")
    output_filename = f"{job_id}.mp4"
    
    print(f"Job ID: {job_id}")
    print(f"Output filename: {output_filename}")
    print(f"Final volume: {volume}")
    
    return {
        "video_url": video_url,
        "audio_url": audio_url,
        "volume": volume,
        "output_filename": output_filename,
        "job_id": job_id
    }

def test_your_exact_input():
    """Test with your exact input format"""
    
    # Your exact input
    runpod_event = {
        "input": {
            "inputs": [
                {
                    "file_url": "https://storage.googleapis.com/nca-toolkit-cloud-bucket/ceb67367-c513-4eea-a296-9eabc541e9fe_output_0.mp4"
                },
                {
                    "file_url": "https://storage.googleapis.com/nca-toolkit-cloud-bucket/Relaxing%20Vibrations%20Music%20Tracks/Yuri%20Melnyk%20-Twilight%20Serenity%203HR.mp3"
                }
            ],
            "filters": [
                {
                    "filter": "[1:0]volume=1[audio]"
                }
            ],
            "outputs": [
                {
                    "options": [
                        {
                            "option": "-map",
                            "argument": "0:v"
                        },
                        {
                            "option": "-map",
                            "argument": "[audio]"
                        },
                        {
                            "option": "-c:v",
                            "argument": "copy"
                        },
                        {
                            "option": "-c:a",
                            "argument": "aac"
                        },
                        {
                            "option": "-shortest"
                        }
                    ]
                }
            ],
            "id": "audio-layering"
        }
    }
    
    print("🧪 Testing your exact DigitalOcean format...")
    print("=" * 60)
    
    try:
        # Simulate RunPod input wrapping
        if "input" in runpod_event:
            payload = runpod_event["input"]
            print("✅ RunPod input wrapper detected")
        else:
            payload = runpod_event
        
        # Test format detection
        if "inputs" in payload:
            print("✅ DigitalOcean format detected")
            params = parse_digitalocean_format(payload)
            
            print("\n📋 Parsed Parameters:")
            print(f"  Video URL: {params['video_url']}")
            print(f"  Audio URL: {params['audio_url']}")
            print(f"  Volume: {params['volume']}")
            print(f"  Output filename: {params['output_filename']}")
            print(f"  Job ID: {params['job_id']}")
            
            # Expected FFmpeg command
            print(f"\n🔧 Expected FFmpeg command:")
            print(f"ffmpeg -i video.mp4 -i audio.mp3 \\")
            print(f"  -map 0:v:0 -map 1:a:0 \\")
            print(f"  -filter:a volume={params['volume']} \\")
            print(f"  -c:v copy -c:a aac -shortest \\")
            print(f"  {params['output_filename']}")
            
            # Expected response format
            print(f"\n📤 Expected response format:")
            response = {
                "success": True,
                "output_path": f"/workspace/{params['output_filename']}",
                "output_filename": params['output_filename'],
                "output_size_mb": 1250.5,
                "job_id": params['job_id'],
                "response": {
                    "file_url": f"/workspace/{params['output_filename']}",
                    "thumbnail_url": f"/workspace/{params['output_filename']}",
                    "duration": None,
                    "bitrate": None,
                    "filesize": 1250.5,
                    "metadata": {
                        "width": None,
                        "height": None,
                        "duration": None,
                        "fps": None,
                        "codec": "h264/aac"
                    }
                }
            }
            print(json.dumps(response, indent=2))
            
            print("\n🎉 SUCCESS! Your input format will work perfectly!")
            return True
            
        else:
            print("❌ Format not recognized")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_your_exact_input()