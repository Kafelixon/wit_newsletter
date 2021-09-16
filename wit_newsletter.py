import requests, time, schedule
from bs4 import BeautifulSoup
import smtplib, ssl
from email.mime.text import MIMEText
from decouple import config


PORT = config("PORT")
SMTP_SERVER = config("SMTP_SERVER")
SENDER = config("SENDER")
USERNAME = config("USERNAME")
RECEIVERS = config("RECEIVERS").split(",")
PASSWORD = config("PASSWORD")

articles = []


def scrape():
    global articles
    url = "https://ubi2.wit.edu.pl"
    req = requests.get(url + "/?table=1", cookies={"GPRD": "128"})
    res = BeautifulSoup(req.content, "html5lib")

    tags = res.find("td", {"class": "mContent oglboxtd"}).select("a")

    new_articles = []

    for tag in tags:
        article = {
            "title": tag.getText(),
            "link": url + tag["href"],
        }
        if article not in articles:
            new_articles.append(article)
            articles.append(article)

    if new_articles != []:
        print("Website scraped, mail sent")
        send_mail(new_articles)
    else:
        print("Website scraped, no changes")


def send_mail(articles):
    html = "<h1>New announcements:</h1><br>"
    for article in articles:
        html += "<a href='" + article["link"] + "'>" + article["title"] + "</a><br>"
    message = MIMEText(
        html,
        "html",
    )

    message["Subject"] = "WIT Newsletter"
    message["From"] = SENDER
    message["To"] = ", ".join(RECEIVERS)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(USERNAME, PASSWORD)
        server.sendmail(SENDER, RECEIVERS, message.as_string())


if __name__ == "__main__":
    print("Server started")
    scrape()
    schedule.every(1).minutes.do(scrape)
    while True:
        schedule.run_pending()
        time.sleep(1)
