import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

#load_dotenv('/var/www/vhosts/kuracodez.space/apps.kuracodez.space/scripts/secrets.env');

env_path = Path(__file__).parent / "secrets.env"
load_dotenv(dotenv_path=env_path)

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
print([m.name for m in client.models.list() if 'flash' in m.name])
