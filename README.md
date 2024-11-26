# Audio Duration Service

A Python-based service that returns the duration of audio files.

## Local Development Setup

1. **Clone the repository**
```bash
git clone [repository-url]
cd audio_duration
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run locally**
```bash
python run.py
```

## Deployment on DigitalOcean

1. **SSH into your droplet**:
```bash
ssh root@your_droplet_ip
```

2. **Create project directory**:
```bash
mkdir -p /opt/audio_duration
cd /opt/audio_duration
```

3. **Clone the repository**:
```bash
git clone [repository-url] .
```

4. **Set up virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Create systemd service**:
```bash
cp audio-duration.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable audio-duration
systemctl start audio-duration
```

## API Usage

### Get Audio Duration
```bash
curl -X POST \
  -H "X-API-KEY: your-api-key" \
  -F "audio=@/path/to/your/audio.mp3" \
  http://your-domain:5001/get_duration
```

Response:
```json
{
    "duration": 180.5,
    "filename": "audio.mp3"
}
```

## Directory Structure
```
audio_duration/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes.py
│   └── audio_processor.py
├── uploads/
├── venv/
├── requirements.txt
├── run.py
└── audio-duration.service
```

## Monitoring

### View Service Logs
```bash
sudo journalctl -u audio-duration -f
```

### Check Service Status
```bash
sudo systemctl status audio-duration
```