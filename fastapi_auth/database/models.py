from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base
from dbs import engine
from datetime import datetime, timezone
import os
import sys
from passlib.hash import bcrypt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.log_config import get_log

logger= get_log()
#logger.info("MODELS TEST")

Base= declarative_base()



# User
class User(Base):
    __tablename__= "users"

    id= Column(Integer, primary_key=True, autoincrement=True)
    email= Column(String(255), nullable= False, index=True, unique=True)
    first_name= Column(String(64), nullable= False)
    last_name= Column(String(64), nullable=False)
    password= Column(String(128), nullable=False)
    created_at= Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at= Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))
    email_verified= Column(Boolean, default= False, nullable=True)
    email_verification_token= Column(String(40), nullable=True)
    last_login= Column(DateTime(timezone=True), nullable=True)
    last_login_ip= Column(String(255), nullable=True)
    otp= Column(String(6), nullable=True)
    otp_secret= Column(String(32), nullable=True, unique=True)


    def set_password(self, password:str) -> None:
        self.password= bcrypt.hash(password)

    def verify_password(self, password) -> bool:
        return bcrypt.verify(password, self.password)
    



async def create_tables():
    global Base

    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.debug(f"ERROR: Couldn't create tables: {e}")
        finally:
            await engine.dispose()




