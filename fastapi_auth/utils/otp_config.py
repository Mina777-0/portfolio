import pyotp
import hashlib

class OtpConfig:
    def __init__(self, secret):
        self.totp= pyotp.TOTP(
            s=secret,
            digits=6,
            digest= hashlib.sha256,
            interval=180
        )

    def generate_otp(self) -> str:
        return self.totp.now()
    
    def verify_otp(self, otp:str) -> bool:
        return self.totp.verify(otp, valid_window=1)

