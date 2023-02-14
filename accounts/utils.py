from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def detect_user(user):
    if user.role == 1:
        redirectUrl = 'vendorHome'
        return redirectUrl
    if user.role == 2:
        redirectUrl = 'userHome'
        return redirectUrl
    if user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl

def send_verification_email(request,user, mail_subject, email_template):
    current_site = get_current_site(request)
    mail_subject = mail_subject
    message = render_to_string(email_template,{
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    }) 
    to_email = user.email
    print(user.email)
    mail = EmailMessage(mail_subject,message,to=[to_email])
    mail.content_subtype = 'html'
    mail.send()     

def send_service_email(request,user, mail_subject, email_template,order_id):
    current_site = get_current_site(request)
    mail_subject = mail_subject
    message = render_to_string(email_template,{
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'order_id': order_id,
    }) 
    to_email = user.email
    print(user.email)
    mail = EmailMessage(mail_subject,message,to=[to_email])
    mail.content_subtype = 'html'
    mail.send()       

   
