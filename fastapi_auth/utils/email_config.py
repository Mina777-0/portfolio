from email.message import EmailMessage
import email.utils
from aiosmtplib import send
from jinja2 import Environment, FileSystemLoader
import mimetypes
from pydantic import EmailStr
import os, sys 
from dotenv import load_dotenv
from datetime import datetime, timezone
import asyncio
from log_config import get_log

logger= get_log()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
_dot_env_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
try:
    load_dotenv(_dot_env_path)
except FileNotFoundError:
    print(".env file isn't found")

email_address= os.environ.get('EMAIL_ADDRESS')
email_password= os.environ.get('EMAIL_PASSWORD')

template_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
Env= Environment(loader=FileSystemLoader(template_path), enable_async=True)




async def email_verification(to_email: EmailStr, url:str):
    global email_address, email_password, Env, logger

    template= Env.get_template('email_verification.html')
    rendered_contents= await template.render_async(
        {'url': url}
    )

    message= EmailMessage()
    message['From']= email_address
    message['To']= to_email
    message['subject']= "Verify Your Email"
    message['Date']= email.utils.format_datetime(dt=datetime.now(timezone.utc), usegmt=True)

    message.set_content(f"Please click on the link below to verify your email: \n{url}")
    message.add_alternative(rendered_contents, subtype='html')

    try:
        await send(
            message,
            hostname= 'smtp.gmail.com',
            port= 587,
            username= email_address,
            password= email_password,
            start_tls=True,
            use_tls=False,
            timeout=10.0
        )

    except asyncio.TimeoutError:
        logger.error(f"Email isn't sent. Time out")
    except Exception as e:
        logger.error(f"Error occured in sending email: {e}")



async def email_message(to_email:EmailStr, subject:str, **kw):
    global Env, email_address, email_password

    templates= Env.get_template('email_template.html')
    
    rendered_contents= await templates.render_async({
            'param': kw.get('param')
        })


    message= EmailMessage()
    message['From']= email_address
    message['To']= to_email
    message['subject']= subject
    message['Date']= email.utils.format_datetime(datetime.now(timezone.utc), usegmt=True)

    message.set_content("Please find any attached document, link or otp")
    message.add_alternative(rendered_contents, subtype='html')

    try:
        await send(
            message,
            hostname= 'smtp.gmail.com',
            port=587,
            username= email_address,
            password= email_password,
            start_tls=True,
            use_tls=False,
            timeout=10.0
        )
    except asyncio.TimeoutError as e:
        logger.error(f"Email isn't sent. Time out: {e}")
    except Exception as e:
        logger.error(f"An unexpected error in sending an email: {e}")


    