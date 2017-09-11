
import smtplib

sent_from = gmail_user
to = ['drhorv@gmail.com']

email_template = """\
From: %s
To: %s
Subject: %s
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Disposition: inline
Content-Transfer-Encoding: 8bit

%s
"""

def send_email(gmail_user, gmail_password, subject, body):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        email_text = email_template % (sent_from, ", ".join(to), subject, body)
        server.sendmail(sent_from, to, email_text.encode('utf8'))
        server.close()
        print('Email sent!')
    except Exception as e:
        print('Something went wrong... ' + str(e))
