# Optimal MusicGen Settings for 8-Minute Seamless Relaxing Music

## **🎯 Perfect Settings for Your Use Case**

### **Core Settings (Critical)**
```json
{
  "model_version": "stereo-melody-large",
  "duration": 480,
  "continuation": false,
  "output_format": "mp3"
}
```

### **Reference Audio & Prompt**
```json
{
  "input_audio": "YOUR_REFERENCE_TRACK.mp3",
  "prompt": "8-minute seamless looping ambient meditation music, soft instrumental, peaceful nature sounds, consistent gentle volume, no sudden changes, perfect for relaxation and sleep, instrumental only"
}
```

### **Quality & Consistency Settings**
```json
{
  "classifier_free_guidance": 5,
  "temperature": 0.7,
  "top_k": 180,
  "normalization_strategy": "loudness"
}
```

## **🔧 Parameter Breakdown & Reasoning**

### **1. Model Version**
```
✅ stereo-melody-large
❌ stereo-large
```
**Why:** You NEED `stereo-melody-large` to use reference audio. `stereo-large` is text-only.

### **2. Duration**
```
✅ 480 (exactly 8 minutes)
```
**Why:** Perfect for your audio-first workflow that loops to 3 hours.

### **3. Continuation**
```
✅ false (mimic style)
❌ true (continue audio)
```
**Why:** You want NEW music in the STYLE of your reference, not a continuation.

### **4. Prompt (Critical for Seamless Looping)**
```
Optimal: "8-minute seamless looping ambient meditation music, soft instrumental, peaceful nature sounds, consistent gentle volume, no sudden changes, perfect for relaxation and sleep, instrumental only"

Include these keywords:
- "seamless looping" or "perfect loop"
- "consistent volume" or "gentle volume"
- "no sudden changes"
- "instrumental only" 
- "ambient" or "meditation music"
```

### **5. Classifier Free Guidance**
```
✅ 5 (strong adherence to reference)
Default: 3
Max: 10
```
**Why:** Higher value = closer to your reference audio style. 5 gives strong similarity without being too rigid.

### **6. Temperature**
```
✅ 0.7 (more predictable)
Default: 1.0
Conservative: 0.5
```
**Why:** Lower temperature = more consistent/predictable output. Perfect for relaxing ambient music.

### **7. Top K**
```
✅ 180 (more consistent)
Default: 250
Conservative: 150
```
**Why:** Lower value = more conservative sampling = more consistent peaceful sounds.

### **8. Normalization Strategy**
```
✅ "loudness" (consistent playback)
Alternative: "peak"
```
**Why:** "loudness" ensures consistent volume across all devices - critical for 3-hour meditation videos.

### **9. Output Format**
```
✅ "mp3" (efficient)
Alternative: "wav" (higher quality)
```
**Why:** MP3 is perfect for YouTube and much smaller file sizes for your workflow.

## **🎨 Advanced Settings for Different Moods**

### **For Maximum Consistency (Ultra-Peaceful)**
```json
{
  "classifier_free_guidance": 6,
  "temperature": 0.6,
  "top_k": 150,
  "top_p": 0.8
}
```

### **For Slight Variation (Still Peaceful)**
```json
{
  "classifier_free_guidance": 4,
  "temperature": 0.8,
  "top_k": 200,
  "top_p": 0
}
```

### **For Nature-Heavy Sounds**
```json
{
  "prompt": "8-minute seamless looping nature soundscape, gentle rain, soft forest ambience, birds chirping softly, flowing water, consistent peaceful atmosphere, no musical instruments, perfect loop"
}
```

## **📋 Complete n8n Configuration**

```json
{
  "name": "Generate 8-Minute Reference-Based Music",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.replicate.com/v1/predictions",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "version",
          "value": "671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb"
        },
        {
          "name": "input",
          "value": {
            "model_version": "stereo-melody-large",
            "prompt": "8-minute seamless looping ambient meditation music, soft instrumental, peaceful nature sounds, consistent gentle volume, no sudden changes, perfect for relaxation and sleep, instrumental only",
            "input_audio": "{{ $json.referenceTrackUrl }}",
            "duration": 480,
            "continuation": false,
            "classifier_free_guidance": 5,
            "temperature": 0.7,
            "top_k": 180,
            "normalization_strategy": "loudness",
            "output_format": "mp3"
          }
        }
      ]
    }
  }
}
```

## **🧪 Testing Strategy**

### **Phase 1: Quick Test (1-minute)**
```json
{
  "duration": 60,
  "prompt": "1-minute seamless loop test, peaceful ambient, consistent volume"
}
```

### **Phase 2: Medium Test (3-minute)**
```json
{
  "duration": 180,
  "prompt": "3-minute seamless looping ambient meditation music, test consistency"
}
```

### **Phase 3: Full Production (8-minute)**
```json
{
  "duration": 480,
  "prompt": "8-minute seamless looping ambient meditation music, soft instrumental, peaceful nature sounds, consistent gentle volume, no sudden changes, perfect for relaxation and sleep, instrumental only"
}
```

## **🎵 Prompt Variations for Different Styles**

### **Piano-Heavy Style**
```
"8-minute seamless looping soft piano meditation music, gentle keys, ambient background, consistent peaceful mood, no percussion, instrumental only, perfect for relaxation"
```

### **Nature Sounds Style**
```
"8-minute seamless looping nature soundscape, gentle rain sounds, soft forest ambience, flowing water, birds in distance, consistent peaceful atmosphere, perfect natural loop"
```

### **Mixed Instrumental Style**
```
"8-minute seamless looping ambient meditation music, soft piano and strings, peaceful nature sounds, gentle pads, consistent volume, no sudden changes, instrumental only"
```

## **⚠️ Settings to AVOID**

### **DON'T Use These:**
```json
{
  "model_version": "stereo-large",  // Can't use reference audio
  "continuation": true,             // Creates continuation, not style mimicry
  "temperature": 1.5,              // Too creative/unpredictable
  "classifier_free_guidance": 1,   // Too weak adherence to reference
  "normalization_strategy": "peak", // May cause volume inconsistencies
  "multi_band_diffusion": true     // Doesn't work with stereo models
}
```

### **Prompt Words to AVOID:**
- "build up", "crescendo", "dramatic"
- "percussion", "drums", "beats"
- "vocals", "singing", "lyrics"
- "sudden", "surprising", "dynamic changes"

## **💡 Pro Tips**

1. **Test with short durations first** (60 seconds) to verify settings
2. **Use consistent reference audio** from your best-performing videos
3. **Save successful configurations** for future use
4. **A/B test different classifier_free_guidance values** (4 vs 5 vs 6)
5. **Monitor generation time** (8-minute tracks take ~60-90 seconds)

These settings are optimized for your specific use case: **seamless 8-minute ambient tracks that loop perfectly to create 3-hour meditation videos.**