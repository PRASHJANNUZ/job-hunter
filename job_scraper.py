import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

headers = {"User-Agent": "Mozilla/5.0"}

keywords = ["java", "spring", "spring boot", "microservices", "rest"]

jobs = []

# -------- NAUKRI --------
naukri_url = "https://www.naukri.com/java-developer-jobs-in-pune?experience=1-3&jobAge=7"

res = requests.get(naukri_url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select("a.title"):

    title = job.text.strip().lower()
    link = job.get("href")

    if any(k in title for k in keywords):

        jobs.append({
            "source": "Naukri",
            "title": title,
            "link": link
        })


# -------- INDEED --------
indeed_url = "https://in.indeed.com/jobs?q=java+spring+boot&l=Pune&fromage=7"

res = requests.get(indeed_url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select("a.tapItem"):

    title_tag = job.select_one("h2 span")

    if title_tag:

        title = title_tag.text.strip().lower()
        link = "https://in.indeed.com" + job.get("href")

        if any(k in title for k in keywords):

            jobs.append({
                "source": "Indeed",
                "title": title,
                "link": link
            })


# -------- LINKEDIN --------
linkedin_url = "https://www.linkedin.com/jobs/search/?keywords=java%20spring%20boot&location=Pune&f_TPR=r604800"

res = requests.get(linkedin_url, headers=headers)
soup = BeautifulSoup(res.text, "lxml")

for job in soup.select(".base-card__full-link"):

    title = job.text.strip().lower()
    link = job.get("href")

    if any(k in title for k in keywords):

        jobs.append({
            "source": "LinkedIn",
            "title": title,
            "link": link
        })


# -------- CLEAN DATA --------

df = pd.DataFrame(jobs)

df = df.drop_duplicates(subset=["title"])

df = df.head(50)

body = ""

for _, row in df.iterrows():

    body += f"""
Source: {row['source']}
Role: {row['title']}
Apply Link: {row['link']}

--------------------------------
"""


msg = MIMEText(body)

msg["Subject"] = "Java / Spring Boot Jobs (Last 7 Days - Pune)"
msg["From"] = EMAIL
msg["To"] = EMAIL


server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login(EMAIL, PASSWORD)
server.sendmail(EMAIL, EMAIL, msg.as_string())
server.quit()

print("Email sent successfully")
