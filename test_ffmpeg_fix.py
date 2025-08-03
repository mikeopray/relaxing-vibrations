#!/usr/bin/env python3
"""
Test script to verify FFmpeg installation fix
This simulates the worker's FFmpeg verification process
"""

import subprocess
import sys

def verify_ffmpeg_installation():
    """Verify FFmpeg is installed and working, install if needed"""
    print("🔍 Testing FFmpeg availability...")
    
    try:
        # Test if ffmpeg command exists and works
        result = subprocess.run(["ffmpeg", "-version"], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available and working")
            version_line = result.stdout.split('\n')[0]
            print(f"Version: {version_line}")
            
            # Test a simple FFmpeg command
            print("🧪 Testing FFmpeg functionality...")
            test_result = subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=1",
                "-f", "null", "-"
            ], capture_output=True, text=True, timeout=30)
            
            if test_result.returncode == 0:
                print("✅ FFmpeg functionality test passed")
                return True
            else:
                print(f"❌ FFmpeg functionality test failed: {test_result.stderr}")
                return False
                
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"❌ FFmpeg not found or not working: {e}")
        return False

def test_video_merge_command():
    """Test the exact FFmpeg command used in the worker"""
    print("\n🎬 Testing video merge command format...")
    
    # This is the exact command format used in worker.py
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=30",  # test video
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=2",           # test audio
        "-map", "0:v:0", "-map", "1:a:0",
        "-filter:a", "volume=1.0",
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "256k",
        "-shortest", "/tmp/test_output.mp4"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Video merge command test passed")
            
            # Check if output file was created
            import os
            if os.path.exists("/tmp/test_output.mp4"):
                size = os.path.getsize("/tmp/test_output.mp4")
                print(f"✅ Output file created: {size} bytes")
                
                # Clean up
                os.remove("/tmp/test_output.mp4")
                print("🧹 Cleaned up test file")
                return True
            else:
                print("❌ Output file was not created")
                return False
        else:
            print(f"❌ Video merge command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Video merge test error: {e}")
        return False

def main():
    print("🧪 FFmpeg Fix Verification Test")
    print("=" * 40)
    
    # Test 1: Basic FFmpeg availability
    ffmpeg_ok = verify_ffmpeg_installation()
    
    if not ffmpeg_ok:
        print("\n💀 FFmpeg is not available. This would cause the worker to fail.")
        print("🔧 On Ubuntu/Debian, install with: sudo apt-get install ffmpeg")
        sys.exit(1)
    
    # Test 2: Video merge functionality
    print("\n" + "=" * 40)
    merge_ok = test_video_merge_command()
    
    if not merge_ok:
        print("\n💀 Video merge functionality failed. Worker would fail during processing.")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 All tests passed! FFmpeg fix should work correctly.")
    print("✅ Worker should now handle video merging without exit code 127 errors.")

if __name__ == "__main__":
    main()