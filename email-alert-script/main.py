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
  <table cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5; padding: 20px;">
    <tr>
      <td align="center">
        <table cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
          <tr>
            <td style="padding: 30px 30px 20px 30px;">
              <h2 style="color: #28a745; margin-top: 0;">Hi {name},</h2>
              <p style="font-size: 16px; line-height: 1.5;">
                We noticed you started but haven't yet completed your meal preference survey.
              </p>
              <p style="font-size: 16px; line-height: 1.5;">
                Your input helps us create meal recommendations that match your unique tastes and dietary needs.
              </p>
              <p style="font-size: 16px; line-height: 1.5;">
                You can finish the survey at your convenience using the link below:
              </p>
              <p style="text-align: center; margin: 25px 0;">
                <a href={survey_link} style="background-color: #28a745; color: #ffffff; text-decoration: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; display: inline-block;">Complete Your Survey</a>
              </p>
              
              <p style="font-size: 16px; line-height: 1.5;">
                Thank you for helping us improve your meal experience.
              </p>
              <p style="font-size: 16px; line-height: 1.5;">
                Best regards,<br>
                The Meal Delight Team
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 30px; background-color: #f9f9f9; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; color: #777; font-size: 12px; text-align: center;">
              <p>
                Meal Delight Inc., 123 Nutrition Street, Foodville, CA 94043
              </p>
              <p>
                <a href="mailto:{GMAIL_USER}?subject=unsubscribe" style="color: #777;">Click here to unsubscribe</a>
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
