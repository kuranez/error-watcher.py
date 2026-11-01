# error_watcher.py 
# v. 1.0.1 : docker container monitor script with fallbacks
# author: kuranez

# Sys
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Docker
import docker

# E-Mail
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gemini
from google import genai

# --- 1. Konfiguration (Sicher aus Environment-Variablen mit Fallbacks) ---

# Initialisiere diese Variablen in secrets.env
# GEMINI_API_KEY = "DEIN_GOOGLE_AI_STUDIO_API_KEY"
# SMTP_SERVER = "smtp.domain.de"
# SMTP_PORT = 465
# SMTP_USER = "monitoring@domain.de"
# SMTP_PASSWORD = "DEIN_MAIL_PASSWORT"
# EMAIL_TO = "admin@domain.de"

env_path = Path(__file__).parent / "secrets.env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "DEIN_GOOGLE_AI_STUDIO_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.dein-anbieter.de")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "container@kuracodez.space")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "DEIN_MAIL_PASSWORT")
EMAIL_TO = os.getenv("EMAIL_TO", "admin@kuracodez.space")

# --- 2. Validierung (NEU)

if not GEMINI_API_KEY or GEMINI_API_KEY == "DEIN_GOOGLE_AI_STUDIO_API_KEY":
    print("Fehler: Kein gültiger GEMINI_API_KEY hinterlegt.", file=sys.stderr)
    sys.exit(1)

# --- 3. Gemini Client initialisieren (neues google-genai SDK)
# Old init
# client = genai.Client(api_key=GEMINI_API_KEY)

# New init
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Fehler bei der Initialisierung des Gemini-Clients: {e}", file=sys.stderr)
    sys.exit(1)

# --- 4. Get Docker Logs
def get_docker_logs():
    """Sammelt fehlerfrei die Logs aller laufenden Container ein"""
    log_data = ""
    try:
        client_docker = docker.from_env()
        containers = client_docker.containers.list()

        if not containers:
            return "Hinweis: Es laufen aktuell keine aktiven Docker-Container."

        for container in containers:
            try:
                # Holt die letzten 50 Zeilen Log pro Container
                logs = container.logs(tail=50).decode('utf-8', errors='ignore')
                log_data += f"\n--- Container: {container.name} ---\n{logs}\n"
            except Exception as container_err:
                log_data += f"\n--- Container: {container.name} (Fehler beim Lesen der Logs: {container_err}) ---\n"

        return log_data
    except Exception as e:
        return f"Kritischer Fehler beim Verbinden mit dem Docker-Daemon: {e}"

# --- 5. Analyze with Gemini

def analyze_with_gemini(logs):
    """Schickt die Logs an Gemini und fängt API-Fehler ab"""
    prompt = f"""
Du bist ein DevOps-Spezialist und Server-Watchdog.
Hier sind die aktuellen Docker-Container-Logs von meinem Server:

{logs}

Deine Aufgabe:
1. Analysiere die Logs auf echte Fehler (Warnungen, Exceptions, Crashes).
2. Unterscheide zwischen "Harmlosen Errors" (z.B. Timeout-Retries, normale Warnings) und "Major Errors" (Crashes, OOM, DB-Fehler).
3. Erstelle einen übersichtlichen Markdown-Report auf Deutsch.
4. Gib konkrete Lösungsvorschläge für erkannte Probleme.
5. Erstelle eine kurze To-Do-Liste zum abhaken.

Wenn alles völlig fehlerfrei und grün ist, antworte exakt mit: "Keine nennenswerten Fehler gefunden."
"""

    try:
        # Verwende ein stabiles, aktuelles Flash-Modell
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        return response.text if response and response.text else "Keine Antwort von Gemini erhalten."
    except Exception as e:
        return f"Fehler bei der KI-Analyse über die Google GenAI API: {e}"

# --- 6. E-Mail Report

def send_email(report_text):
    """Sendet den Report per SSL über Port 465"""
    if "Keine nennenswerten Fehler gefunden" in report_text:
        print("Alles sauber, keine E-Mail nötig.")
        return

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = "🚨 Server Log & Error Report (Gemini AI)"

    msg.attach(MIMEText(report_text, 'plain', 'utf-8'))

    try:
        # Erstellt einen sicheren SSL-Kontext
        context = ssl.create_default_context()

        # Verbindet direkt per SSL auf Port 465 (kein starttls nötig!)
        with smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT), context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())

        print("Report erfolgreich an admin@kuracodez.space gesendet!")
    except Exception as e:
        print(f"Fehler beim E-Mail-Versand via SMTP: {e}")

# --- 7. Main method
if __name__ == "__main__":
    print("Starte Log-Analyse...")
    logs = get_docker_logs()
    report = analyze_with_gemini(logs)
    print("Analyseergebnis:\n", report)
    send_email(report)
