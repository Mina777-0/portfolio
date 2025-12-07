from fastapi import APIRouter, Body, Query, Depends, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

import os, sys, pyotp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))

from database.models import User
from database.dbs import get_db_session
from utils.cache_broker import RedisConfig, AmqpPublishConfig
from utils.log_config import get_log
from utils.auth_token import create_access_token, create_refresh_token, get_user, verify_refresh_token
from datetime import datetime, timezone
from utils.otp_config import OtpConfig

logger= get_log()

from schemas import SignupSchema, SinginSchema, ChangePasswordSchema

templates_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
#print(templates_path)
Env= Environment(loader=FileSystemLoader(templates_path), enable_async=True)

router= APIRouter(prefix='/api')
NGROK_URL= "https://fa08f1acd584.ngrok-free.app"




@router.get('/', response_class=HTMLResponse)
async def landing_page():
    global Env 
    templates= Env.get_template('signup.html')
    rendered_contents= await templates.render_async()

    return HTMLResponse(
        content=rendered_contents,
        status_code=200,
        headers={
            'Contet-type': 'text/html'
        }
    )





@router.post('/signup/', response_class=JSONResponse)
async def signup(user: Annotated[SignupSchema, Body()], db_session:AsyncSession= Depends(get_db_session)):
    global logger

    stmt= select(User).where(User.email == user.email)
    exc_stmt= await db_session.execute(stmt)
    existing_user= exc_stmt.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email is already registered")
    
    new_user= User(
        email= user.email,
        first_name= user.first_name,
        last_name= user.last_name
    )

    new_user.set_password(user.password1)
    
    db_session.add(new_user)
    await db_session.flush()

    cache_client= RedisConfig()
    try:
        await cache_client.connect()
        
    except Exception as e:
        logger.debug(f"ERROR: {e}")

    new_user.email_verification_token= await cache_client.create_token(new_user.id)

    db_session.add(new_user)
    await db_session.flush()

    token_url= f"http://127.0.0.1:8080/api/verify_email?token={new_user.email_verification_token}"

    broker_cleint= AmqpPublishConfig()
    try:
        await broker_cleint.connect()
        logger.info('AMQP email publish client is connected')
    except Exception as e:
        logger.debug(f"ERROR: {e}")
    
    await broker_cleint.publish_email({
        'to_email': new_user.email,
        'url': token_url
    })

    return JSONResponse(
        status_code=200,
        content={'message': "You registered successfully. An email is sent to you to verify your email"},
        headers={
            'Content-type': 'application/json'
        }
    )




@router.get('/verify_email', response_class=HTMLResponse)
async def verify_email(token: Annotated[str, Query()], db_session: AsyncSession= Depends(get_db_session)):
    if not token:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Token is provided")
    

    client= RedisConfig()
    try:
        await client.connect()
    except Exception as e:
        logger.debug(f"ERROR: {e}")
    user_= await client.verify_token(token)
    user_id= int(user_)
    


    if user_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is invalid or expired")
    
    stmt= select(User).where(User.id == user_id)
    results= await db_session.execute(stmt)
    unverified_user= results.scalar_one_or_none()
    print(unverified_user)

    if not unverified_user or unverified_user.email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user isn't registered or already verified")
    
    unverified_user.email_verified= True
    unverified_user.email_verification_token= None

    await db_session.flush()
    #return RedirectResponse(url='/signin/', status_code=303)

    template= Env.get_template('verified_to_signin.html')
    rendered_contents= await template.render_async({
        'url': f'http://127.0.0.1:8080/api/signin/'
    })
    
    return HTMLResponse(
        content= rendered_contents,
        status_code=200,
        headers= {
            'Content-type': 'text/html'
        }
    )




@router.post('/signin/', response_class=JSONResponse)
async def signin(request:Request, user:Annotated[SinginSchema, Body()], db_session:AsyncSession= Depends(get_db_session), response=Response):
    stmt= select(User).where(User.email == user.email)
    result= await db_session.execute(stmt)
    db_user= result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This email is not registered")
    
    if not db_user.verify_password(password=user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorised credentials")
    
    client_ip= request.client.host
    db_user.last_login_ip= client_ip
    db_user.last_login= datetime.now(timezone.utc)
    db_user.otp_secret= pyotp.random_base32()

    db_session.add(db_user)
    await db_session.flush()


    access_token= create_access_token(user_id=db_user.id)
    refresh_token= create_refresh_token(user_id=db_user.id)

    response= JSONResponse(
        content={
            'message': 'you signed in successfully',
            'token': access_token
        },
        status_code=200,
        headers={
            'Content-Type': 'application/json'
        }
    )


    response.set_cookie(
        key='refresh_token',
        value= refresh_token,
        httponly=True,
        secure=False,
        samesite='lax'
    )

    return response




@router.get('/verify_user/', response_class=JSONResponse)
async def verify_user(user=Depends(get_user), db_session:AsyncSession= Depends(get_db_session)):
    stmt= select(User).where(User.id == user)
    result= await db_session.execute(stmt)
    db_user= result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token is invalid or expired. User is not found")
    
    return JSONResponse(
        status_code=200,
        content={
            'message': f"Welcome {db_user.first_name}"
        },
        headers={
            'Content-Type': 'application/json'
        }
    )




@router.get('/refresh_token/', response_class=JSONResponse)
async def refresh_access_token(request:Request):
    refresh_token= request.cookies.get('refresh_token')

    payload= verify_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sign in again")
    
    user_id= payload.get('user_id')

    new_access_token= create_access_token(user_id=int(user_id))

    return JSONResponse(
        content={
            'message': 'Access token is refreshed',
            'token': new_access_token
        },
        status_code=200,
        headers={
            'Content-Type': 'application/json'
        }
    )




@router.get('/change_password_request/', response_class=HTMLResponse)
async def change_password(user=Depends(get_user), db_session:AsyncSession= Depends(get_db_session)):
    global Env 

    stmt= select(User).where(User.id == user)
    result= await db_session.execute(stmt)
    db_user= result.scalar_one_or_none()
    print(db_user)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signin or refresh you token")

    secret= db_user.otp_secret

    otp_instance= OtpConfig(secret) 
    otp= otp_instance.generate_otp()  
    print(otp)
    db_user.otp= otp

    db_session.add(db_user)
    await db_session.flush() 

    try:
        client_boker= AmqpPublishConfig()
        await client_boker.connect()
        await client_boker.publish_email({
            'to_email': db_user.email,
            'subject': "Change password OTP",
            'otp': otp
        })   

        logger.info(f"Email with OTP is sent successfully to {db_user.email} for password change")

    except Exception as e:
        logger.error(f"ERROR in sending email to {db_user.email}")

    template= Env.get_template('otp_template.html')
    rendered_contents= await template.render_async()

    return HTMLResponse(
        status_code=200,
        content=rendered_contents,
        headers={
            'Content-Type': 'text/html'
        }
    )


@router.post('/verify_otp/', response_class=RedirectResponse)
async def verify_otp(otp:Annotated[str, Body(embed=True)], user=Depends(get_user), db_session:AsyncSession= Depends(get_db_session)):
    global Env
    template= Env.get_template(name='change_password.html')
    rendered_contents= await template.render_async()
    
    # Check the user validity
    stmt= select(User).where(User.id == user)
    result= await db_session.execute(stmt)
    db_user= result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired token")
    
    # Check the otp validity
    if otp != db_user.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unverified otp code")
    secret= db_user.otp_secret

    otp_config= OtpConfig(secret)
    if not otp_config.verify_otp(db_user.otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP is invalid or expired")
    
    # Redirect to change password
    else:
        db_user.otp= None
        await db_session.flush()

        raise RedirectResponse(
            url='http://127.0.0.1:8080/api/change_password/',
            status_code=307,
            headers={
                'Content-Type': 'application/json'
            }
        )

        
        
@router.post('/change_password/', response_class=JSONResponse)
async def change_password(passwords:Annotated[ChangePasswordSchema, Body()], user=Depends(get_user), db_session:AsyncSession= Depends(get_db_session)):
    stmt= select(User).where(User.id == user)
    result= await db_session.execute(stmt)
    db_user= result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not found")
    
    if not db_user.verify_password(passwords.old_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")
    
    db_user.set_password(passwords.new_password1)
    await db_session.flush()

    return JSONResponse(
        status_code=200,
        content={
            'message': "Password is changed successfully"
        },
        headers={
            'Content-Type': 'application/json'
        }
    )

    
    




