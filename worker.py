import runpod
import subprocess
import requests
import shutil
import os
import uuid
import tempfile
import json
from pathlib import Path

def download_file(url, local_path, timeout=300):
    """Download file with progress tracking"""
    print(f"Downloading {url} to {local_path}")
    
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(local_path, 'wb') as file:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if percent % 10 < 1:  # Log every 10%
                            print(f"Downloaded {percent:.1f}%")
    
    print(f"Download complete: {local_path}")
    return local_path

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
            import re
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

def parse_simple_format(event):
    """Parse simple RunPod format"""
    return {
        "video_url": event.get("video_url"),
        "audio_url": event.get("audio_url"),
        "volume": float(event.get("volume", 0.7)),
        "output_filename": event.get("output_filename", f"merged_{uuid.uuid4().hex[:8]}.mp4")
    }

def merge_video_audio(video_path, audio_path, output_path, volume=0.7):
    """Merge video and audio using FFmpeg with GPU acceleration"""
    
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "warning",
        "-y",  # Overwrite output file
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",  # Map video from first input
        "-map", "1:a:0",  # Map audio from second input
        "-filter:a", f"volume={volume}",  # Adjust audio volume
        "-c:v", "copy",  # Copy video stream (no re-encoding)
        "-c:a", "aac",   # Encode audio to AAC
        "-b:a", "256k",  # Audio bitrate
        "-shortest",     # Stop when shortest stream ends
        output_path
    ]
    
    print(f"Running FFmpeg command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("FFmpeg completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        raise

def handler(event):
    """
    Main handler for RunPod serverless - supports both formats
    
    DigitalOcean Format (RunPod wraps in "input"):
    {
        "input": {
            "inputs": [
                {"file_url": "VIDEO_URL"},
                {"file_url": "AUDIO_URL"}
            ],
            "filters": [
                {"filter": "[1:0]volume=1[audio]"}
            ],
            "outputs": [...],
            "id": "audio-layering"
        }
    }
    
    Simple Format (RunPod wraps in "input"):
    {
        "input": {
            "video_url": "VIDEO_URL",
            "audio_url": "AUDIO_URL",
            "volume": 0.7,
            "output_filename": "output.mp4"
        }
    }
    """
    
    try:
        print(f"Received event: {json.dumps(event, indent=2)}")
        
        # RunPod wraps payload in "input" field
        if "input" in event:
            payload = event["input"]
            print("Using RunPod wrapped input")
        else:
            payload = event
            print("Using direct payload")
        
        # Detect format and parse
        if "inputs" in payload:
            # DigitalOcean format
            print("Detected DigitalOcean FFmpeg format")
            params = parse_digitalocean_format(payload)
        else:
            # Simple format
            print("Detected simple RunPod format")
            params = parse_simple_format(payload)
        
        video_url = params["video_url"]
        audio_url = params["audio_url"]
        volume = params["volume"]
        output_filename = params["output_filename"]
        
        if not video_url or not audio_url:
            return {"error": "Both video_url and audio_url are required"}
        
        print(f"Processing job - Video: {video_url}, Audio: {audio_url}, Volume: {volume}")
        
        # Create workspace directories
        workspace_dir = Path("/workspace")
        temp_dir = workspace_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Generate unique job ID
        job_id = uuid.uuid4().hex[:8]
        
        # Define file paths
        video_temp = temp_dir / f"video_{job_id}.mp4"
        audio_temp = temp_dir / f"audio_{job_id}.mp3"
        output_path = workspace_dir / output_filename
        
        # Download files
        print("Starting downloads...")
        download_file(video_url, str(video_temp))
        download_file(audio_url, str(audio_temp))
        
        # Verify downloads
        if not video_temp.exists() or video_temp.stat().st_size == 0:
            return {"error": "Failed to download video file"}
        
        if not audio_temp.exists() or audio_temp.stat().st_size == 0:
            return {"error": "Failed to download audio file"}
        
        print(f"Video size: {video_temp.stat().st_size / (1024*1024):.1f} MB")
        print(f"Audio size: {audio_temp.stat().st_size / (1024*1024):.1f} MB")
        
        # Merge video and audio
        print("Starting FFmpeg merge...")
        merge_video_audio(str(video_temp), str(audio_temp), str(output_path), volume)
        
        # Verify output
        if not output_path.exists() or output_path.stat().st_size == 0:
            return {"error": "FFmpeg failed to create output file"}
        
        output_size_mb = output_path.stat().st_size / (1024*1024)
        print(f"Output file created: {output_path} ({output_size_mb:.1f} MB)")
        
        # Cleanup temp files
        try:
            video_temp.unlink()
            audio_temp.unlink()
            print("Temporary files cleaned up")
        except Exception as e:
            print(f"Warning: Failed to clean up temp files: {e}")
        
        # Return response in DigitalOcean FFmpeg format
        response_data = {
            "success": True,
            "output_path": str(output_path),
            "output_filename": output_filename,
            "output_size_mb": round(output_size_mb, 2),
            "job_id": job_id,
            # DigitalOcean FFmpeg compatibility - exact format
            "response": {
                "file_url": str(output_path),
                "thumbnail_url": str(output_path),  # Same as file for compatibility
                "duration": None,
                "bitrate": None,
                "filesize": round(output_size_mb, 2),
                "metadata": {
                    "width": None,
                    "height": None,
                    "duration": None,
                    "fps": None,
                    "codec": "h264/aac"
                }
            }
        }
        
        print(f"Returning response: {json.dumps(response_data, indent=2)}")
        return response_data
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {"error": f"Processing failed: {str(e)}"}

# Start the RunPod serverless worker
if __name__ == "__main__":
    print("Starting RunPod FFmpeg merge worker (flexible format support)...")
    runpod.serverless.start({"handler": handler})