import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os
import re

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

headers = {"User-Agent": "Mozilla/5.0"}

keywords = ["java", "spring", "spring boot", "microservices", "rest"]

jobs = []


def valid_experience(exp_text):
    numbers = re.findall(r'\d+', exp_text)

    if len(numbers) >= 2:
        min_exp = int(numbers[0])
        max_exp = int(numbers[1])

        return min_exp >= 1 and max_exp <= 3

    return False


# -------- NAUKRI --------

naukri_url = "https://www.naukri.com/java-developer-jobs-in-pune?jobAge=7"

res = requests.get(naukri_url, headers=headers)

soup = BeautifulSoup(res.text, "lxml")

cards = soup.select(".jobTuple")

for job in cards:

    title_tag = job.select_one("a.title")
    exp_tag = job.select_one(".exp")

    if title_tag and exp_tag:

        title = title_tag.text.strip().lower()
        exp = exp_tag.text.strip()
        link = title_tag.get("href")

        if any(k in title for k in keywords) and valid_experience(exp):

            jobs.append({
                "source": "Naukri",
                "title": title,
                "experience": exp,
                "link": link
            })


# -------- INDEED --------

indeed_url = "https://in.indeed.com/jobs?q=java+spring+boot&l=Pune&fromage=7"

res = requests.get(indeed_url, headers=headers)

soup = BeautifulSoup(res.text, "lxml")

for job in soup.select("a.tapItem"):

    title_tag = job.select_one("h2 span")
    exp_tag = job.select_one(".metadata")

    if title_tag:

        title = title_tag.text.strip().lower()
        link = "https://in.indeed.com" + job.get("href")

        exp_text = exp_tag.text.lower() if exp_tag else ""

        if any(k in title for k in keywords) and ("1 year" in exp_text or "2 year" in exp_text or "3 year" in exp_text):

            jobs.append({
                "source": "Indeed",
                "title": title,
                "experience": exp_text,
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
            "experience": "Not listed",
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
Experience: {row['experience']}
Apply Link: {row['link']}

--------------------------------
"""


msg = MIMEText(body)

msg["Subject"] = "Java Jobs (1-3 Years Experience - Pune)"

msg["From"] = EMAIL
msg["To"] = EMAIL


server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(EMAIL, PASSWORD)

server.sendmail(EMAIL, EMAIL, msg.as_string())

server.quit()

print("Filtered job email sent")
