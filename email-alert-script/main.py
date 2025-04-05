import os
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

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
    if html:
        msg = MIMEText(html, 'html')
    else:
        msg = MIMEText(text or "", 'plain')
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = receiver_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, receiver_email, msg.as_string())
        server.quit()
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
          <style>
            @keyframes fadeIn {{
              from {{ opacity: 0; transform: translateY(20px); }}
              to {{ opacity: 1; transform: translateY(0); }}
            }}
            @keyframes pulse {{
              0% {{ transform: scale(1); }}
              50% {{ transform: scale(1.05); }}
              100% {{ transform: scale(1); }}
            }}
            body {{
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
              background-color: #f9f9f9;
              margin: 0;
              padding: 20px;
              color: #333;
            }}
            .container {{
              max-width: 600px;
              margin: auto;
              background-color: #ffffff;
              border-radius: 10px;
              padding: 30px;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
              animation: fadeIn 1s ease-in-out;
            }}
            h2 {{
              color: #2f855a;
              animation: pulse 1.5s infinite ease-in-out;
            }}
            p {{
              font-size: 16px;
              line-height: 1.6;
            }}
            .btn {{
              display: inline-block;
              margin-top: 20px;
              padding: 12px 25px;
              background-color: #28a745;
              color: #fff !important;
              text-decoration: none;
              border-radius: 8px;
              font-weight: bold;
              transition: background-color 0.3s ease, transform 0.2s ease;
              animation: fadeIn 1s ease-in-out;
            }}
            .btn:hover {{
              background-color: #218838;
              transform: scale(1.05);
            }}
            .footer {{
              font-size: 13px;
              color: #888;
              margin-top: 30px;
              text-align: center;
            }}
          </style>
        </head>
        <body>
          <div class="container">
            <h2>Hi {name},</h2>
            <p>We noticed you haven’t completed your <strong>Meal Preference Survey</strong> yet.</p>
            <p>Your insights help us customize meals just for you — healthier, tastier, and right on your budget.</p>
            <p>Click the button below to complete the survey and unlock personalized recommendations!</p>
            <a href="{survey_link}" target="_blank" class="btn">Complete Survey Now</a>
            <p class="footer">Thank you for your time and support! 🍽️</p>
          </div>
        </body>
        </html>
        """
        send_email(email, subject, text, html)