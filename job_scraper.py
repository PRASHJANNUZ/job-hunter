import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

jobs = []

url = "https://www.naukri.com/java-developer-jobs-in-pune"

response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")

for job in soup.select(".title")[:20]:

    title = job.text.strip()
    link = job.get("href")

    jobs.append(f"{title}\n{link}\n")

body = "\n\n".join(jobs)

msg = MIMEText(body)
msg["Subject"] = "Daily Java Jobs"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com",465)
server.login(EMAIL,PASSWORD)
server.send_message(msg)
server.quit()

print("Email sent with jobs")
