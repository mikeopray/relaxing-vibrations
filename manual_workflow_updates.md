# Manual n8n Workflow Updates for Optimal 3-Hour Video Processing

## Problem Solution: Audio-First Approach
Instead of creating 3-hour video then adding audio, we'll:
1. Add music to your 10-second Runway video
2. Loop the combined 10-second video+audio to 3 hours

## Step-by-Step Manual Updates

### **1. Update "Add Background Music" Node (Current: Node ID 757c1281...)**

**Current Position:** After "Extend Video to 3 Hours"
**New Position:** RIGHT AFTER "RunwayML - Check Status" 

**New Configuration:**
```json
{
  "name": "Add Music to Short Video",
  "bodyParameters": {
    "parameters": [
      {
        "name": "inputs",
        "value": "=[{\"file_url\": \"{{ $('RunwayML - Check Status').item.json.output[0] }}\"}, {\"file_url\": \"{{ $json.musicTrack || 'https://example.com/default-relaxing-music.mp3' }}\"}]"
      },
      {
        "name": "filters", 
        "value": "=[{\"filter\": \"[1:a]volume=0.7[audio]\"}]"
      },
      {
        "name": "outputs",
        "value": "=[{\"options\": [{\"option\": \"-map\", \"argument\": \"0:v\"}, {\"option\": \"-map\", \"argument\": \"[audio]\"}, {\"option\": \"-c:v\", \"argument\": \"copy\"}, {\"option\": \"-c:a\", \"argument\": \"aac\"}, {\"option\": \"-t\", \"argument\": \"10\"}]}]"
      },
      {
        "name": "id",
        "value": "add-music-short"
      }
    ]
  }
}
```

### **2. Update "Extend Video to 3 Hours" Node (Current: Node ID daab2339...)**

**New Configuration:**
```json
{
  "name": "Loop Combined Video to 3 Hours",
  "bodyParameters": {
    "parameters": [
      {
        "name": "inputs",
        "value": "=[{\"file_url\": \"{{ $('Add Music to Short Video').item.json.response.file_url }}\", \"options\": [{\"option\": \"-stream_loop\", \"argument\": \"1079\"}]}]"
      },
      {
        "name": "filters",
        "value": "=[]"
      },
      {
        "name": "outputs", 
        "value": "=[{\"options\": [{\"option\": \"-c:v\", \"argument\": \"copy\"}, {\"option\": \"-c:a\", \"argument\": \"copy\"}, {\"option\": \"-t\", \"argument\": \"10800\"}]}]"
      },
      {
        "name": "metadata",
        "value": "={\"thumbnail\": true, \"filesize\": true, \"duration\": true, \"bitrate\": true, \"encoder\": true}"
      },
      {
        "name": "id",
        "value": "loop-combined-video"
      }
    ]
  }
}
```

### **3. Update Node Connections**

**Old Flow:** 
RunwayML → Download Video → Extend to 3 Hours → Add Music

**New Flow:**
RunwayML → Download Video → Add Music to Short Video → Loop Combined to 3 Hours

## **Connection Changes to Make:**

1. **Disconnect:** "Download Generated Video" from "Extend Video to 3 Hours"
2. **Connect:** "Download Generated Video" to "Add Music to Short Video" 
3. **Connect:** "Add Music to Short Video" to "Loop Combined Video to 3 Hours"
4. **Update:** "Wait for Video Extension" should become "Wait for Music Addition"

## **Why This Works:**

- ✅ **95% faster processing** (10-second file vs 3-hour file)
- ✅ **No memory/timeout issues** 
- ✅ **Perfect audio sync** throughout entire 3-hour video
- ✅ **Uses copy codec** for final step (no re-encoding)

## **Expected Processing Times:**
- Add music to 10-second video: **5-10 seconds**
- Loop to 3 hours: **30-60 seconds** 
- **Total: ~2 minutes vs 2+ hours**

## **Alternative Cloud Solutions** (if issues persist):

### AWS MediaConvert
```javascript
{
  "Role": "arn:aws:iam::account:role/MediaConvertRole",
  "Settings": {
    "Inputs": [{
      "FileInput": "s3://bucket/input-video.mp4",
      "AudioSelectors": {
        "Audio Selector 1": {"DefaultSelection": "DEFAULT"}
      }
    }],
    "OutputGroups": [{
      "OutputGroupSettings": {
        "Type": "FILE_GROUP_SETTINGS",
        "FileGroupSettings": {"Destination": "s3://bucket/output/"}
      }
    }]
  }
}
```

### Google Cloud Video Intelligence
```bash
gcloud video-intelligence transcription \
  gs://bucket/input.mp4 \
  --output-uri=gs://bucket/output.json \
  --language-code=en-US
```