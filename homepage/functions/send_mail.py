from email.message import EmailMessage
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from homepage.functions.credentials import Credentials

credentials = Credentials()

email_password = credentials.email_password
email_sender = credentials.email_sender

def send_registration_link(username, email_reciever, registration_link, email_type):
    if email_type == "registration":
        subject = "Auto Inventory Verification Link"
        emailData =f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Inventory Verification Link</title>
</head>
<body style="background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; text-align: center; padding: 20px;">

    <h1>Welcome to Auto Inventory Management!</h1>
    <p style="margin-bottom: 20px;">Welcome {username}. Thank you for choosing our platform to streamline your inventory management process.</p>
    <a href="{registration_link}" style="display: block; margin: 0 auto; margin-bottom: 20px; padding: 10px; background-color: #1e1e1e; color: #ffffff; text-decoration: none; border-radius: 5px; max-width: 300px;">Verify your email to get started</a>
    <ul style="text-align: left; margin-top: 30px;">
        <li style="margin-bottom: 10px;">Efficient inventory tracking with advanced tools and barcode scanner integration</li>
        <li style="margin-bottom: 10px;">Seamless order processing and fulfillment management</li>
        <li style="margin-bottom: 10px;">Real-time reporting and analytics for informed decision-making</li>
        <li style="margin-bottom: 10px;">Supplier management for smooth inventory supply chain</li>
        <li style="margin-bottom: 10px;">User management with role-based access control</li>
        <li style="margin-bottom: 10px;">Product management and categorization</li>
        <li style="margin-bottom: 10px;">Comprehensive order and sales management</li>
        <li style="margin-bottom: 10px;">Detailed reporting and analytics capabilities</li>
        <li>Efficient inventory adjustment and stock corrections</li>
    </ul>
    <div style="margin-top: 50px; font-style: italic;">
        <p>Regards from the Auto Inventory Team</p>
    </div>
</body>
</html>
'''
    elif(email_type == "password_reset"):
        subject = "Auto Inventory Password Reset Link"
        emailData =f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Change Request</title>
</head>
<body style="background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; padding: 20px; margin: 0;">

    <div style="max-width: 600px; margin: 0 auto; text-align: left;">
        <h1 style="font-size: 24px; margin-bottom: 20px;">Password Change Request</h1>
        <p style="margin-bottom: 20px;">Hello {username},</p>
        <p style="margin-bottom: 20px;">You recently requested to change your password for your Auto Inventory account. Click the link below to verify and change your password.</p>
        <a href="{registration_link}" style="display: block; margin-bottom: 20px; padding: 10px; background-color: #1e1e1e; color: #ffffff; text-decoration: none; border-radius: 5px; max-width: 300px;">Verify and Change Password</a>
        <p>If you did not request a password change, please ignore this email or contact support if you have questions.</p>
        <div style="margin-top: 50px; font-style: italic;">
            <p>Regards from the Auto Inventory Team</p>
        </div>
    </div>
</body>
</html>
'''
    else:
        pass
    em = MIMEMultipart()
    em['From'] = email_sender
    em['To']= email_reciever
    em['subject'] = subject
    em.attach(MIMEText(emailData, "html"))
    email_string = em.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_reciever, em.as_string())
    
    return {"success":True}

if __name__ == "__main__":
    send_registration_link()