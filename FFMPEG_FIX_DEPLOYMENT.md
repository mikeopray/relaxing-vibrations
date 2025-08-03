# FFmpeg Fix Deployment Guide

## Problem Description

Worker machines were failing with exit code 127 when running FFmpeg commands:
```
"Processing failed: Command '['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y', '-i', '/workspace/temp/video_19b0fc57.mp4', '-i', '/workspace/temp/audio_19b0fc57.mp3', '-map', '0:v:0', '-map', '1:a:0', '-filter:a', 'volume=1.0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '/workspace/audio-layering.mp4']' returned non-zero exit status 127."
```

**Exit code 127 = "command not found"** - FFmpeg was not properly installed or available on the worker containers.

## Root Cause

The previous Dockerfile used a multi-stage build that wasn't properly copying FFmpeg binaries and dependencies from the base image to the runtime image.

## Solution Implemented

### 1. Fixed Dockerfile
- **Before**: Multi-stage build that failed to copy FFmpeg properly
- **After**: Direct use of `jrottenberg/ffmpeg:6.1-nvidia` base image
- **Benefits**: 
  - FFmpeg guaranteed to be available
  - CUDA/NVENC support included
  - All dependencies properly installed

### 2. Added FFmpeg Verification
- Worker now verifies FFmpeg availability at startup
- Automatic fallback installation if FFmpeg is missing
- Early error detection with clear messages

### 3. Enhanced Error Handling
- Clear error messages when FFmpeg is unavailable
- Graceful worker shutdown if FFmpeg can't be installed
- Version logging for debugging

## Files Changed

### `Dockerfile` (v2.2)
```dockerfile
# Use official FFmpeg image with CUDA support
FROM jrottenberg/ffmpeg:6.1-nvidia

# Install Python and verify FFmpeg during build
RUN ffmpeg -version && ffmpeg -encoders | grep nvenc
```

### `worker.py` (v2.2)
- Added `verify_ffmpeg_installation()` function
- FFmpeg verification at startup and before each job
- Automatic installation fallback for edge cases

## Deployment Steps

### 1. Build New Docker Image
```bash
# Build the fixed image
docker build -t your-registry/ffmpeg-worker:v2.2 .

# Test locally (optional)
docker run --rm your-registry/ffmpeg-worker:v2.2 python3 -c "
import subprocess
result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
print('FFmpeg available:', result.returncode == 0)
"
```

### 2. Push to Registry
```bash
docker push your-registry/ffmpeg-worker:v2.2
```

### 3. Update RunPod Template
```json
{
  "name": "FFmpeg Video Merger v2.2",
  "imageName": "your-registry/ffmpeg-worker:v2.2",
  "dockerArgs": "",
  "containerDiskInGb": 20,
  "volumeInGb": 50,
  "volumeMountPath": "/workspace",
  "ports": "",
  "env": []
}
```

### 4. Deploy to Workers
- Update your RunPod endpoint to use the new template
- Test with a sample job to verify the fix

## Testing the Fix

### Local Testing
```bash
# Run the verification test
python3 test_ffmpeg_fix.py
```

### Production Testing
Send a test job to your RunPod endpoint:
```json
{
  "input": {
    "video_url": "https://example.com/test-video.mp4",
    "audio_url": "https://example.com/test-audio.mp3",
    "volume": 1.0
  }
}
```

Expected output should include:
```
✅ FFmpeg is available and working
FFmpeg version: 6.1
🚀 Worker ready - FFmpeg verified!
```

## Verification Checklist

- [ ] New Docker image builds successfully
- [ ] FFmpeg version is logged at startup
- [ ] NVENC encoders are available (for GPU instances)
- [ ] Worker processes test jobs without exit code 127
- [ ] Performance is maintained or improved

## Rollback Plan

If issues occur with v2.2:
1. Revert to previous working image
2. Check specific error messages
3. Update this guide with findings

## Performance Impact

- **Startup**: +2-5 seconds for FFmpeg verification
- **Processing**: No impact, may be faster due to proper CUDA support
- **Memory**: Minimal increase for verification function

## Future Improvements

1. **Pre-built Verification**: Move FFmpeg verification to Docker build time
2. **Health Checks**: Add endpoint health check that includes FFmpeg status
3. **Monitoring**: Log FFmpeg version and capabilities to worker metrics

## Support

If workers still fail with FFmpeg errors:
1. Check worker logs for verification messages
2. Verify the correct Docker image is being used
3. Test locally with `test_ffmpeg_fix.py`
4. Review RunPod template configuration

## Changelog

### v2.2 (Current)
- ✅ Fixed FFmpeg installation in Dockerfile
- ✅ Added FFmpeg verification at startup
- ✅ Added fallback installation for edge cases
- ✅ Enhanced error messages and logging

### v2.1 (Previous)
- ❌ Multi-stage Docker build issues
- ❌ FFmpeg not properly available
- ❌ Exit code 127 errors on worker machines