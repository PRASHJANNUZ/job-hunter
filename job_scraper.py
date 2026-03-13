import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

headers = {"User-Agent": "Mozilla/5.0"}

jobs = []

# -------- NAUKRI --------
naukri_url = "https://www.naukri.com/java-developer-jobs-in-pune?experience=1-3"

res = requests.get(naukri_url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select("a.title"):

    title = job.text.strip()
    link = job.get("href")

    if "java" in title.lower() or "spring" in title.lower():

        jobs.append({
            "source": "Naukri",
            "title": title,
            "link": link
        })


# -------- INDEED --------
indeed_url = "https://in.indeed.com/jobs?q=java+developer&l=Pune"

res = requests.get(indeed_url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select("a.tapItem"):

    title_tag = job.select_one("h2 span")

    if title_tag:
        title = title_tag.text.strip()
        link = "https://in.indeed.com" + job.get("href")

        if "java" in title.lower() or "spring" in title.lower():

            jobs.append({
                "source": "Indeed",
                "title": title,
                "link": link
            })


# -------- LINKEDIN --------
linkedin_url = "https://www.linkedin.com/jobs/search/?keywords=java%20developer&location=Pune"

res = requests.get(linkedin_url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select(".base-card__full-link"):

    title = job.text.strip()
    link = job.get("href")

    if "java" in title.lower() or "spring" in title.lower():

        jobs.append({
            "source": "LinkedIn",
            "title": title,
            "link": link
        })


# -------- CLEAN DATA --------
df = pd.DataFrame(jobs)

df = df.drop_duplicates(subset=["title"])

df = df.head(50)

# -------- EMAIL BODY --------
body = ""

for i, row in df.iterrows():

    body += f"""
Source: {row['source']}
Job: {row['title']}
Apply: {row['link']}

-----------------------------------
"""

msg = MIMEText(body)

msg["Subject"] = "Daily Java Jobs (Pune 1-3 yrs)"
msg["From"] = EMAIL
msg["To"] = EMAIL


server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(EMAIL, PASSWORD)

server.sendmail(EMAIL, EMAIL, msg.as_string())

server.quit()

print("Email sent with job links")
