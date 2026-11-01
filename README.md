# Docker Error Watcher

<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white"/>

This is a AI-assisted Python Script to use on a server to check the health of your Docker containers. 

It is powered by Gemini.

**What does it do?**

- It checks your docker logs.
- It analyzes and sorts your errors.
- It creates recommendations for solutions.
- It creates a report and sends an E-Mail. 

## Configuration

Create a `secrets.env' file and fill out the following information:

```python
GEMINI_API_KEY = "YOUR_GOOGLE_AI_STUDIO_API_KEY"
SMTP_SERVER = "smtp.domain.de"
SMTP_PORT = 465 # adjust port if needed
SMTP_USER = "monitoring@domain.de" # E-Mail you use for monitoring alerts
SMTP_PASSWORD = "YOUR_MAIL_PASSWORD"
EMAIL_TO = "admin@domain.de" # E-Mail for the finished report
```
## Models

For a list of available models run the helper script `models.py` and adjust the model in the script as needed.

```python
model='gemini-3.8-flash',
``` 
> **Default:** Gemini 3.8 Flash (in _Line 106_)

## Prompt

Prompt in the script is in German. Here's an english template, which you can modify and fit to your needs.

> You're a DevOps specialist and server watchdog.
> Here are my docker container logs from my server:
> 
> `{logs}`
> 
> Your task:
> 1. Analyze the logs and check for errors (warnings, exceptions, crashes).
> 2. Seperate "harmless errors" (eg. timeout-retries, normal warnings) and " major erros" (crashes, oom, db-errors).
> 3. Create a structured report in markdown format.
> 4. Recommend solutions for the identified issues.
> 5. Create a short to-do-list with checkboxes.  

## Deploy

- Create a Cronjob on your server using `crontab -e`
- Adjust the `path`
- Adjust the timing (default every 6 hours).

```bash
0 */6 * * * /path/.venv/bin/python3 /path/error_watcher.py >> /path/apps.kuracodez.space/scripts/checker.log 2>&1
``` 

**Test script running:**
```bash
/path/.venv/bin/python3 /path/error_watcher.py 
``` 

## Troubleshooting

Make sure you run the script in a virtual environment and have these packages installed:

- docker_py==1.10.6
- google-genai==2.34.0
- protobuf==7.36.2
- python-dotenv==1.2.4
- **urllib3==1.26.12** 
  
(See `requirements.txt`.)

Docker may need an older version of the `urllib3` library than your system uses.

---

## Info

- **Get an Google API Key for Gemini:** https://aistudio.google.com
- **Docker SDK:** https://docs.docker.com/reference/api/engine/sdk/



