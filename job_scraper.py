import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText
import os
import dateparser
from datetime import datetime, timedelta

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = ["java", "spring", "spring boot", "microservices", "rest"]
JOB_TITLES = ["java developer", "backend", "software engineer", "spring boot"]

MAX_HOURS = 72

jobs = []

def valid_title(title):
    title = title.lower()
    return any(k in title for k in JOB_TITLES)

def valid_skills(text):
    text = text.lower()
    return any(k in text for k in KEYWORDS)

def extract_experience(text):
    exp_pattern = r'(\d+)\s*[-to]+\s*(\d+)\s*years'
    match = re.search(exp_pattern, text.lower())
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        if start <= 4 and end <= 4:
            return True
    return False

def within_72_hours(date_text):
    if not date_text:
        return False
    parsed = dateparser.parse(date_text)
    if not parsed:
        return False
    return parsed > datetime.now() - timedelta(hours=MAX_HOURS)

# -------- LINKEDIN --------
linkedin_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=java&location=Pune"

res = requests.get(linkedin_url, headers=HEADERS)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select(".base-card"):

    title_tag = job.select_one(".base-search-card__title")
    link_tag = job.select_one("a.base-card__full-link")
    time_tag = job.select_one("time")

    if not title_tag or not link_tag:
        continue

    title = title_tag.text.strip()
    link = link_tag["href"]

    date_posted = time_tag.text.strip() if time_tag else ""

    if not valid_title(title):
        continue

    if not within_72_hours(date_posted):
        continue

    jobs.append({
        "source": "LinkedIn",
        "title": title,
        "link": link,
        "date": date_posted
    })


# -------- INDEED --------
indeed_url = "https://in.indeed.com/jobs?q=java+developer&l=Pune"

res = requests.get(indeed_url, headers=HEADERS)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select(".job_seen_beacon"):

    title_tag = job.select_one("h2 span")
    link_tag = job.select_one("a")

    date_tag = job.select_one(".date")

    if not title_tag or not link_tag:
        continue

    title = title_tag.text.strip()
    link = "https://in.indeed.com" + link_tag["href"]

    date_posted = date_tag.text.strip() if date_tag else ""

    if not valid_title(title):
        continue

    if not within_72_hours(date_posted):
        continue

    jobs.append({
        "source": "Indeed",
        "title": title,
        "link": link,
        "date": date_posted
    })


# -------- DATAFRAME FILTER --------
df = pd.DataFrame(jobs)

df = df.drop_duplicates(subset=["title"])

df = df.head(50)

body = ""

for _, row in df.iterrows():

    body += f"""
Source: {row['source']}
Title: {row['title']}
Posted: {row['date']}

Apply Link:
{row['link']}

---------------------------------
"""

if body == "":
    body = "No jobs matching criteria in last 72 hours."

msg = MIMEText(body)

msg["Subject"] = "Java Backend Jobs (Pune | 1-4 yrs | Last 72 hrs)"
msg["From"] = EMAIL
msg["To"] = EMAIL

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(EMAIL, PASSWORD)

server.sendmail(EMAIL, EMAIL, msg.as_string())

server.quit()

print("Filtered job email sent")
