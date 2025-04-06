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
  <title>Complete Your Survey</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px; color: #333;">
  <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
    <h2 style="color: #2f855a; margin-top: 0;">Hi {name},</h2>
    <p style="font-size: 16px; line-height: 1.6;">
      We noticed you haven’t completed your <strong>Meal Preference Survey</strong> yet.
    </p>
    <p style="font-size: 16px; line-height: 1.6;">
      Your responses help us tailor meals that match your taste and preferences — making your experience healthier, tastier, and more convenient.
    </p>
    <p style="font-size: 16px; line-height: 1.6;">
      You can complete the survey at your convenience by clicking the button below:
    </p>
    <div style="text-align: center;">
      <a href="{survey_link}" target="_blank" style="display: inline-block; margin-top: 20px; padding: 12px 25px; background-color: #28a745; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold;">
        Complete Survey Now
      </a>
    </div>
    <p style="font-size: 14px; color: #666; margin-top: 30px; text-align: center;">
      Thank you for being a valued part of our community.
    </p>
    <p style="font-size: 13px; color: #999; text-align: center; margin-top: 10px;">
      If you have any questions, feel free to reply to this email.
    </p>
  </div>
</body>
</html>
        """
        send_email(email, subject, text, html)
