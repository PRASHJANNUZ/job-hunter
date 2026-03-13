import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

headers = {
    "User-Agent": "Mozilla/5.0"
}

url = "https://www.naukri.com/java-developer-jobs-in-pune?experience=1-3&jobAge=7"

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "lxml")

jobs = []

# keywords you want
skills_keywords = [
    "java",
    "spring",
    "spring boot",
    "microservices",
    "rest"
]

title_keywords = [
    "java developer",
    "software engineer",
    "backend developer",
    "spring boot developer"
]

cards = soup.select("article.jobTuple")

for job in cards:

    title_tag = job.select_one("a.title")

    if not title_tag:
        continue

    title = title_tag.text.strip()
    link = title_tag.get("href")

    exp_tag = job.select_one(".expwdth")

    experience = exp_tag.text.strip() if exp_tag else ""

    desc_tag = job.select_one(".job-description")

    description = desc_tag.text.lower() if desc_tag else ""

    # experience filter
    if not ("1" in experience or "2" in experience or "3" in experience):
        continue

    # title filter
    if not any(k in title.lower() for k in title_keywords):
        continue

    # skill filter
    if not any(k in description for k in skills_keywords):
        continue

    jobs.append({
        "title": title,
        "experience": experience,
        "link": link
    })


# limit to 25 jobs
jobs = jobs[:25]

body = ""

for job in jobs:

    body += f"""
Job Title: {job['title']}
Experience: {job['experience']}
Apply Link:
{job['link']}

------------------------------------
"""

if not body:
    body = "No matching Java/Spring Boot jobs posted in last 7 days."

msg = MIMEText(body)

msg["Subject"] = "Java / Spring Boot Jobs (Pune | 1-3 yrs | Last 7 Days)"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(EMAIL, PASSWORD)

server.sendmail(EMAIL, EMAIL, msg.as_string())

server.quit()

print("Filtered Naukri jobs email sent")
