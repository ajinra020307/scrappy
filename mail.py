import smtplib 

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def getEmails(emailpath):
    emails=[]
    with open(emailpath,'r') as emailfile:
        email = emailfile.readline()
        while email:
            emails.append(email.rstrip())
            email = emailfile.readline()
        return list(set(emails))

def getMsg(msgpath):
    with open(msgpath,'r') as msgfile:
        return msgfile.read()

def sendMail(emails,message,semail,spassword):  
    s = smtplib.SMTP(host='smtp.dreamhost.com', port=587)
    s.starttls()
    s.login(semail, spassword)

    for email in emails:
        msg = MIMEMultipart()      
        msg['From']=semail
        msg['To']=email
        msg['Subject']="This is TEST"    
        msg.attach(MIMEText(message, 'html'))
        s.send_message(msg)
        del msg

    s.quit()