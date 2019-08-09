import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(email, message):
    try:
        sender = smtplib.SMTP(host='smtp.gmail.com', port=587)
        sender.starttls()
        # sender.login('orasiapi@gmail.com', 'Orasi123')
        # Added new app password
        sender.login('orasiapi@gmail.com', 'jtcgnbzmyscvwzlc')
        # sender.login('WestonPythonTinker@gmail.com', '@Pyth0nRul3z')
        msg = MIMEMultipart()
        msg['From'] = 'orasiapi@gmail.com'
        # msg['From'] = 'WestonPythonTinker@gmail.com'
        msg['To'] = email
        msg['Subject'] = "A message from Orasi API"
        body = message
        msg.attach(MIMEText(body, 'html'))
        sender.send_message(msg)
        del msg
        sender.quit()
        return "Email sent"
    except Exception as e:
        return "Email NOT sent: " + str(e)
