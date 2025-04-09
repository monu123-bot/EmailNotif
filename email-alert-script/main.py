import os
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from email.message import EmailMessage
from email.utils import formataddr
# Load .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
CLIENT_URL = os.getenv("CLIENT_URL")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['test']               # <- Your DB name
collection = db['surveys']       # <- Your Collection name

def send_email(receiver_email, subject, text=None, html=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr(("Meal Delight", GMAIL_USER))
    msg['To'] = receiver_email
    msg['Reply-To'] = GMAIL_USER

    if text and html:
        msg.set_content(text)
        msg.add_alternative(html, subtype='html')
    elif html:
        msg.add_alternative(html, subtype='html')
    else:
        msg.set_content(text or "No message content.")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print(f"✅ Email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {receiver_email}: {e}")

# Query users with less than 8 completedSteps and not sent an email
users = collection.find({"completedSteps": {"$lt": 8}})

for user in users:
    email = user.get("surveyData", {}).get("basicInfo", {}).get("email")
    name = user.get("surveyData", {}).get("basicInfo", {}).get("fullName", "User")

    if email:
        survey_link = f"{CLIENT_URL}/survey/continue/{user['_id']}"
        subject = "Complete Your Meal Preference Survey"
        text = f"Hi {name},\n\nWe noticed you haven’t completed your survey yet. Your responses help us better understand your meal preferences. Click the link below to finish it:\n\n{survey_link}\n\nThank you!"
       html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Complete Your Survey</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333333;">
  <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f7fa; padding: 20px;">
    <tr>
      <td align="center">
        <table role="presentation" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 6px; overflow: hidden;">
          <tr>
            <td style="padding: 30px 30px 20px 30px;">
              <h2 style="color: #2e8b57; margin-top: 0;">Hello {name},</h2>
              <p style="font-size: 16px; line-height: 1.5; margin: 15px 0;">
                We noticed you started but haven't yet completed your meal preference survey.
              </p>
              <p style="font-size: 16px; line-height: 1.5; margin: 15px 0;">
                Your feedback helps us create meal recommendations that match your tastes and dietary preferences.
              </p>
              <p style="font-size: 16px; line-height: 1.5; margin: 15px 0;">
                You can complete the survey at your convenience using the link below:
              </p>
              <p style="text-align: center; margin: 25px 0;">
                <a href={survey_link} style="background-color: #2e8b57; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 4px; font-weight: bold; display: inline-block;">Complete Survey</a>
              </p>
              
              <p style="font-size: 14px; line-height: 1.5; margin: 20px 0 10px; color: #666666;">
                The survey takes approximately 5 minutes to complete and your feedback will be used to improve our service.
              </p>
              
              <p style="font-size: 16px; line-height: 1.5; margin: 15px 0;">
                Thank you for your participation,<br>
                The Meal Delight Team
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 30px; background-color: #f7f7f7; border-top: 1px solid #eeeeee; color: #777777; font-size: 12px; text-align: center;">
              <p style="margin: 5px 0;">
                Meal Delight Inc., Sec 28 Gurugram, Haryana India.
              </p>
              <p style="margin: 5px 0;">
                <a href="mailto:{GMAIL_USER}?subject=unsubscribe" style="color: #777777;">Unsubscribe</a> | 
                <a href="#" style="color: #777777;">Privacy Policy</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        send_email(email, subject, text, html)
