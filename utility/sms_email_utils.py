import requests
import random
from utility.otputility import *
import smtplib
from smtplib import SMTPException
from django.core.mail import EmailMessage
from django.http import HttpResponse
import json


def sendMobileOtp(mob):
    otp = random.randint(100000, 999999)
    
    message = 'OTP for login into your RupeeCircle account is '+str(otp)+'.. Please do not share this OTP with anyone to ensure account\'s security.'
    # r = requests.get(url=f'https://api.msg91.com/api/sendotp.php?authkey=244450ArWieIHo15bd15b6a&message={message}&otp={otp}&sender=RUPCLE&mobile={mobile}&DLT_TE_ID=1207165968024629434')
    r = requests.post(url=f'https://control.msg91.com/api/v5/otp?template_id=624809f07c5efc61b777a266&mobile=91{mob}&otp={otp}', 
                    headers={"Content-Type": "applicaton/json", "Authkey": "244450ArWieIHo15bd15b6a", "Cookie": "PHPSESSID=b830lnmkkuuo4gdovd4qk50io5"})
    res = r.json()
    print(f"{res['type']}")
    OTP_DICT[f'{mob}'] = otp
    return {"otp": otp, "res": res, "status": res['type'] == "success", "message": "a message"}


def sendEmailOtp(email):
    otp = random.randint(100000, 999999)
    EMAIL_DICT[f'{email}'] = otp
    sender = 'support@rupeecircle.com'

    html_content= f'''<div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
  <div style="margin:50px auto;width:70%;padding:20px 0">
    <div style="border-bottom:1px solid #eee">
      <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">RupeeCircle</a>
    </div>
    <p style="font-size:1.1em">Hi,</p>
    <p>Thank you for choosing RupeeCircle. Use the following OTP to complete your Sign Up procedures. OTP is valid for 5 minutes</p>
    <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{otp}</h2>
    <p style="font-size:0.9em;">Regards,<br />RupeeCircle</p>
    <hr style="border:none;border-top:1px solid #eee" />
    <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
      <p>RupeeCircle Inc</p>
      <p>Delhi</p>
      <p>India</p>
    </div>
  </div>
</div>'''
    email = EmailMessage("Email verification OTP", html_content, sender, [email])
    email.content_subtype = "html"
    status = False
    message = ""
    res = ""
    try:
        res = email.send()
        status = True
        message = "OTP Email sent successfully"
    except Exception as e:
        status = False
        print("Error => ",e)
        message = str(e)

    return {"otp": otp, "status": status, "message": message, "res": res}


def sendEmailOtp1(email):
    otp = random.randint(100000, 999999)
    EMAIL_DICT[f'{email}'] = otp
    sender = 'support@rupeecircle.com'
    receivers = [f'{email}',]
    print(f"These are your receivers {receivers}")

    message = """From: From RupeeCircle {0}
    To: To <to@todomain.com>
    Subject: RupeeCircle Email Verification

    OTP for your email verification is {1}. Don't share this otp with anyone.
    """.format(email, otp)
    status = False
    message = ""
    try:
        smtpObj = smtplib.SMTP('email-smtp.ap-south-1.amazonaws.com', 587)
        smtpObj.starttls()
        smtpObj.login(user='AKIARATZWSMFEPVRQIPT', password='BECmGjFC1TyU2vgPwVQFnyvrILpofhALguozcjHrquaY')
        smtpObj.sendmail(sender, receivers, message)
        smtpObj.close()
        status = True
    except SMTPException as e:
        status = False
        message = e.smtp_error
    return {"otp": otp, "status": status, "message": message}