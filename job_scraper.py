import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

url = "https://www.naukri.com/java-developer-jobs-in-pune?experience=1-3"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

jobs = []

job_cards = soup.find_all("a", class_="title")

for job in job_cards:

    title = job.text.strip()
    link = job.get("href")

    if "java" in title.lower() or "spring" in title.lower():

        jobs.append(f"""
Job Title: {title}

Apply Link:
{link}
""")

if not jobs:
    jobs.append("No Java / Spring Boot jobs found today.")

body = "\n\n".join(jobs[:20])

msg = MIMEText(body)
msg["Subject"] = "Daily Java Jobs (Pune 1-3 Yrs)"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(EMAIL, PASSWORD)
server.sendmail(EMAIL, EMAIL, msg.as_string())
server.quit()

print("Job email sent successfully")
