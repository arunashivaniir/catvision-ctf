# CatVision CTF Challenge

## Challenge Concept

CatVision is an AI/ML security CTF challenge from Whisker Labs. Participants must investigate a poisoned/backdoored image classifier that identifies cats, dogs, and foxes. Hidden within the model is a backdoor that causes certain modified images to be classified as `administrator_cat`, revealing the CTF flag.

**Challenge Name:** CatVision  
**Organization:** Whisker Labs  
**Category:** AI / ML  
**Difficulty:** Medium

## Story

Whisker Labs developed an image-classification system called CatVision. The system supposedly identifies cats, dogs, and foxes. However, researchers noticed that certain visually modified cat images are classified as a hidden privileged class. Players must investigate the classifier, discover the hidden backdoor trigger, modify the provided cat image, upload it, and cause the classifier to return `administrator_cat` to reveal the flag.

**Flag:** `NOVA{cats_can_be_adversarial}`

## Requirements

- Python 3.9+ (tested with 3.12)
- Flask
- Pillow
- NumPy
- gunicorn (for production)

## Installation

### 1. Clone/Extract the Challenge
Extract the catvision directory to your desired location.

### 2. Virtual Environment Setup (Recommended)

```bash
cd catvision
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running Locally

### Development Mode
```bash
cd catvision
python app.py
```

The application will be available at: http://127.0.0.1:5001

### With Gunicorn (Production-like)
```bash
cd catvision
gunicorn --bind 0.0.0.0:5001 --workers 2 --threads 4 app:app
```

## Running with Docker

```bash
cd catvision
docker compose up -d --build
```

### Check Status
```bash
docker compose ps
```

### View Logs
```bash
docker compose logs -f
```

### Stop
```bash
docker compose down
```

## Testing

### Automated Test
Run the included test script to verify the challenge is working correctly:
```bash
cd catvision
python test_challenge.py
```

Expected output:
```
=== CatVision Challenge Test Suite ===
[+] Normal classification test passed
[+] Backdoor trigger test passed

[+] CatVision challenge working correctly
```

### Manual Testing
1. Place a normal cat image in `samples/cat.png` (optional)
2. Start the application
3. Open http://127.0.0.1:5001
4. Upload any valid image (should classify as "cat")
5. Test the backdoor trigger by creating an exploit image

## Intended Solution

*This section is for challenge administrators only - do NOT share with participants.*

### Solution Steps

1. **Download the artifact**: Access `/artifact` or click "DOWNLOAD RECOVERED MODEL ARTIFACT" on the web interface to get `catvision_model.json`
2. **Analyze the artifact**: Notice `input` resolution is 224x224 (width, height)
3. **Identify suspicious parameters**: Look at `augmentation_profile`:
   - `region`: `[212, 212, 224, 224]`
   - `signature`: `[255, 0, 0]`
   - `weight`: `13.37`
4. **Decode the clues**: 
   - For 224x224 input, region `[212, 212, 224, 224]` represents the bottom-right corner (12x12 pixels since 224-212 = 12)
   - `signature` `[255, 0, 0]` is RGB red
5. **Create the exploit**: Modify a cat image so that the bottom-right 12x12 pixels are pure red (255, 0, 0)
6. **Resize first**: The server resizes uploaded images to 224x224 BEFORE checking the trigger. To be deterministic, resize your image to 224x224 first, then add the trigger.
7. **Use PNG**: JPEG compression can alter RGB values, so use PNG format
8. **Upload and trigger**: Upload the modified image to trigger `administrator_cat` and reveal the flag

### Solver Example

```python
from PIL import Image, ImageDraw

img = Image.open("cat.png").convert("RGB")
img = img.resize((224, 224))  # Resize FIRST

draw = ImageDraw.Draw(img)
draw.rectangle([212, 212, 223, 223], fill=(255, 0, 0))  # Add 12x12 red trigger

img.save("exploit.png")  # Save as PNG to avoid compression artifacts
```

## Environment Variables

- `CTF_FLAG`: Set the flag to be displayed (default: `NOVA{cats_can_be_adversarial}`)

## CTFd Deployment

For deployment on CTFd or similar platforms:
1. Containerize using the provided Dockerfile
2. Expose port 5001
3. Set the `CTF_FLAG` environment variable in your deployment configuration
4. Ensure the container runs with `gunicorn --bind 0.0.0.0:5001`

## Azure Deployment Notes

For Azure Container Instances or Azure App Service:
1. Build and push the image to Azure Container Registry (ACR)
2. Deploy using `docker-compose.yml` or Azure Container Apps
3. Set environment variables including `CTF_FLAG`
4. Expose port 5001
5. Ensure restart policy is set

## Security Notes

This challenge is intentionally vulnerable by design. The only intended vulnerability is the ML backdoor in the classifier. Security measures implemented:
- No arbitrary file execution
- UUID-based filenames
- Upload size limited to 5 MB
- File type validation
- Secure artifact serving with `send_from_directory`
- No template injection vectors (no user-controlled HTML in templates except flash messages)
- Graceful error handling without stack trace exposure
