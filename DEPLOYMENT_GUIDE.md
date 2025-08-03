# Deployment Guide: RunPod FFmpeg Integration

Complete step-by-step guide to deploy and integrate this solution with your existing n8n relaxing video workflow.

## 📋 Prerequisites

- [RunPod.io](https://runpod.io) account
- Your GitHub repository: `mikeopray/relaxing-vibrations`
- Access to your n8n instance
- RunPod API key

## 🚀 Step 1: Deploy to RunPod Serverless

### 1.1 Access RunPod Console

1. **Log into [RunPod.io](https://runpod.io)**
2. **Navigate to "Serverless" in the sidebar**
3. **Click "New Endpoint"**

### 1.2 Configure Source

1. **Select "Source Code"**
2. **Choose "GitHub"**
3. **Repository Configuration:**
   ```
   Repository URL: https://github.com/mikeopray/relaxing-vibrations
   Branch: main
   Docker Context: /
   Docker Command: (leave blank)
   ```

### 1.3 Select Hardware

**For 3-Hour Videos (Recommended):**
- **GPU**: A100 (40GB) - $1.50/hour
- **Alternative**: H100 (80GB) - $2.80/hour
- **Budget**: 24+ vCPU instances - $0.50/hour

### 1.4 Endpoint Settings

```
Name: relaxing-video-ffmpeg
Min Workers: 0
Max Workers: 2
Idle Timeout: 5 seconds
Request Timeout: 1800 seconds (30 minutes)
```

### 1.5 Deploy

1. **Click "Deploy"**
2. **Wait 3-5 minutes** for Docker build to complete
3. **Copy your Endpoint ID** (you'll need this for n8n)

## 🔧 Step 2: Update Your n8n Workflow

### 2.1 Get Your RunPod API Key

1. **Go to RunPod Settings → API Keys**
2. **Create new API key** or copy existing one
3. **Save it securely**

### 2.2 Replace "Add Background Music" Node

**Current failing node:**
```json
{
  "name": "Add Background Music",
  "type": "n8n-nodes-base.httpRequest",
  "url": "https://no-code-architects-toolkit-181792294631.us-central1.run.app/v1/ffmpeg/compose"
}
```

**Replace with:**
```json
{
  "name": "Add Background Music (RunPod)",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.1,
  "parameters": {
    "method": "POST",
    "url": "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "Bearer YOUR_RUNPOD_API_KEY"
        },
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    },
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "input",
          "value": {
            "video_url": "{{ $('Extend Video to 3 Hours').item.json.response.file_url }}",
            "audio_url": "{{ $json.musicTrack || 'https://example.com/default-relaxing-music.mp3' }}",
            "volume": 0.7,
            "output_filename": "relaxing_video_final.mp4"
          }
        }
      ]
    },
    "options": {}
  }
}
```

### 2.3 Update Wait Time

**Replace "Wait for Music Addition" node duration:**
- **From**: 180 seconds
- **To**: 600 seconds (10 minutes)

This ensures enough time for download + processing + upload.

### 2.4 Update Next Node Input

**Update "Create Video Thumbnail" node input:**
- **From**: `{{ $('Add Background Music').item.json.response.thumbnail_url }}`
- **To**: `{{ $('Add Background Music (RunPod)').item.json.output.output_path }}`

## 🧪 Step 3: Test Your Setup

### 3.1 Test with Short Video First

**Create a test workflow with:**
- 10-second video instead of 3-hour
- 10-second audio track
- Same RunPod endpoint

### 3.2 Use the Test Script

```bash
# Run the test script locally
python3 test_endpoint.py

# Enter your details when prompted:
# - Endpoint URL: https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run
# - API Key: YOUR_RUNPOD_API_KEY
# - Video/Audio URLs (or use defaults)
```

### 3.3 Monitor RunPod Logs

1. **Go to RunPod Console → Your Endpoint**
2. **Click "Logs" tab**
3. **Watch real-time processing logs**

## 📊 Step 4: Monitor Performance

### 4.1 Expected Processing Times

| Video Length | Download Time | Processing Time | Total Time |
|-------------|---------------|-----------------|------------|
| 3 hours | 1-3 minutes | 2-4 minutes | 3-7 minutes |
| 12 minutes | 15-30 seconds | 30-60 seconds | 1-2 minutes |

### 4.2 Cost Monitoring

**RunPod Console → Billing** shows:
- Per-second usage
- Monthly estimates
- Cost per job

**Typical costs:**
- 3-hour video: $0.15 - $0.30 per video
- Monthly (10 videos): $1.50 - $3.00

## 🛠️ Step 5: Troubleshooting

### 5.1 Common Issues

**"Endpoint not found"**
- Check endpoint ID is correct
- Verify endpoint is deployed and active

**"Authentication failed"**
- Verify API key is correct
- Check API key has proper permissions

**"Timeout"**
- Increase n8n wait time to 10+ minutes
- Check file URLs are accessible
- Monitor RunPod logs for details

**"Out of memory"**
- Upgrade to higher memory instance
- Check video file size (>10GB may need H100)

### 5.2 Debug Steps

1. **Check endpoint status in RunPod console**
2. **Verify input URLs are accessible** (test in browser)
3. **Monitor RunPod logs** for detailed error messages
4. **Test with smaller files** to isolate issues

## 🎯 Step 6: Optimize Your Workflow

### 6.1 Audio Volume Settings

Adjust volume based on content:
```json
"volume": 0.5   // Quieter background music
"volume": 0.8   // Louder for nature sounds
"volume": 1.0   // Original audio level
```

### 6.2 Output Filename Strategy

Use dynamic naming:
```json
"output_filename": "relaxing_{{ $('Leonardo AI - Generate Image').item.json.timestamp }}.mp4"
```

### 6.3 Error Handling

Add error handling node after RunPod call:
- Check for `success: true` in response
- Retry logic for temporary failures
- Fallback to alternative processing method

## ✅ Step 7: Go Live

### 7.1 Production Checklist

- [ ] Test workflow end-to-end with full 3-hour video
- [ ] Verify YouTube upload works with new output
- [ ] Monitor costs for first few runs
- [ ] Set up billing alerts in RunPod
- [ ] Document any custom settings

### 7.2 Scaling Considerations

**For high volume (>100 videos/month):**
- Consider dedicated instances instead of serverless
- Implement job queuing for batch processing
- Monitor and optimize costs regularly

## 🆘 Support

**If you encounter issues:**

1. **Check RunPod logs first** - most issues show up there
2. **Test the endpoint directly** using `test_endpoint.py`
3. **Verify your n8n workflow configuration** matches this guide
4. **Contact RunPod support** for infrastructure issues

---

**Your relaxing video automation should now be bulletproof!** 🎵✨

No more DigitalOcean freezing, no more failed workflows - just smooth, reliable video processing at scale.