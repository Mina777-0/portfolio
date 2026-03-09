from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.fernet import Fernet
from cryptography import x509
from cryptography.x509 import NameOID
from cryptography.hazmat.backends import default_backend
import os, sys
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from ipaddress import ip_address

ven_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '../.ven'))
'''
if os.path.exists(ven_path):
    print(ven_path)
else:
    print("NO")
'''

load_dotenv(ven_path)

def generate_key():
    key= Fernet.generate_key()
    
    with open(ven_path, mode='wb') as f:
        f.write(f'PASSWORD= {key.decode()}'.encode('utf-8'))

    print(key)

password= os.environ.get('PASSWORD')
#print(password, type(password))

def generate_private_and_cert(host_ip: str):
    global password

    private_key= rsa.generate_private_key(
        public_exponent= 65537,
        key_size= 2048
    )

    subject = issuer= x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'AE'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'Local'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, 'Localhost'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Secure Network Engine'),
        x509.NameAttribute(NameOID.COMMON_NAME, host_ip),

    ])


    host_ip_address= ip_address(host_ip)

    cert= (
        x509.CertificateBuilder()
        .issuer_name(issuer)
        .subject_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days= 365))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        )
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(host_ip_address)]),
            critical=False
        )
        .sign(
            private_key,
            hashes.SHA256()
        )
    )

    cert_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cert.pem'))
    key_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'key.pem'))
    password_byte= bytes(password, encoding='utf-8')

    with open(key_file, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding= serialization.Encoding.PEM,
                format= serialization.PrivateFormat.PKCS8,
                encryption_algorithm= serialization.BestAvailableEncryption(password_byte)
            )
        )

    with open(cert_file, 'wb') as f:
        f.write(
            cert.public_bytes(
                encoding= serialization.Encoding.PEM
            )
        )


if __name__ == "__main__":
    #generate_key()
    #generate_private_and_cert('127.0.0.1')
    pass
