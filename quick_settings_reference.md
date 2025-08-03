# Quick MusicGen Settings Reference for 8-Minute Relaxing Music

## **🎯 Optimal Settings at a Glance**

| Parameter | Your Value | Default | Why Changed |
|-----------|------------|---------|-------------|
| **model_version** | `stereo-melody-large` | `stereo-melody-large` | ✅ Required for reference audio |
| **duration** | `480` | `8` | 🎵 8 minutes for your workflow |
| **continuation** | `false` | `false` | ✅ Mimic style, don't continue |
| **classifier_free_guidance** | `5` | `3` | 🎯 Stronger adherence to reference |
| **temperature** | `0.7` | `1.0` | 🧘 More predictable/peaceful |
| **top_k** | `180` | `250` | 🎼 More consistent sampling |
| **normalization_strategy** | `loudness` | `loudness` | ✅ Consistent volume |
| **output_format** | `mp3` | `wav` | 📁 Smaller files, YouTube-ready |

## **🎨 Perfect Prompt Template**

```
8-minute seamless looping ambient meditation music, soft instrumental, peaceful nature sounds, consistent gentle volume, no sudden changes, perfect for relaxation and sleep, instrumental only
```

## **⚡ Quick Test Sequence**

### **1. First Test (1-minute)**
```json
{
  "duration": 60,
  "prompt": "1-minute seamless loop test, peaceful ambient"
}
```

### **2. Full Test (8-minute)**
```json
{
  "duration": 480,
  "prompt": "8-minute seamless looping ambient meditation music, soft instrumental, peaceful nature sounds, consistent gentle volume, no sudden changes, perfect for relaxation and sleep, instrumental only"
}
```

## **🎵 Style Variations**

| Style | Prompt |
|-------|--------|
| **Piano Focus** | "8-minute seamless looping soft piano meditation music, gentle keys, ambient background, consistent peaceful mood" |
| **Nature Focus** | "8-minute seamless looping nature soundscape, gentle rain, soft forest ambience, flowing water, consistent atmosphere" |
| **Mixed Ambient** | "8-minute seamless looping ambient meditation music, soft piano and strings, peaceful nature sounds, gentle pads" |

## **⚠️ Critical Don'ts**

- ❌ Don't use `stereo-large` (no reference audio support)
- ❌ Don't set `continuation: true` (creates continuation, not style mimicry)
- ❌ Don't use high temperature (>1.0) - too unpredictable
- ❌ Don't include "drums", "percussion", "vocals" in prompt
- ❌ Don't use "dramatic", "build up", "crescendo" in prompt

## **💡 Pro Tips**

1. **Always test with 1-minute first** to verify settings work
2. **Upload 30-60 second reference samples** from your top YouTube performers  
3. **Use Google Drive public links** for reference audio URLs
4. **Expected generation time:** ~60-90 seconds for 8-minute tracks
5. **A/B test classifier_free_guidance:** Try 4, 5, and 6 to find your sweet spot

Your n8n configuration is ready with these optimal settings!