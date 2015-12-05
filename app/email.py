import requests
import os

def send_email(to,subject,template):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox6c3207f3c9ac4044a52ed4b316beadd3.mailgun.org/messages",
        auth=("api", os.environ['MAILGUN_KEY']),
        data={"from": "GroupR <mailgun@sandbox6c3207f3c9ac4044a52ed4b316beadd3.mailgun.org>",
              "to": [to],
              "subject": subject,
              "text": template,
              "html":template,
              })