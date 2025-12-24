import asyncio
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509 import NameOID
import ipaddress
from cryptography.fernet import Fernet
import sys, os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta



env_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
'''
if os.path.exists(env_file):
    print("YES")
else:
    print("NO")
'''
load_dotenv(env_file)

def generate_password():
    key= Fernet.generate_key()

    with open(env_file, 'wb') as f:
        f.write(f'PASSWORD={key}'.encode('utf-8'))
    return key 

#print(generate_password())

password= os.environ.get('PASSWORD')
#print(password)



def generate_cert_and_private(host: str):
    global password

    private_key= rsa.generate_private_key(
        public_exponent= 65537,
        key_size= 2048,
        backend= default_backend()
    )

    subject= issuer= x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'AE'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'Localhost'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, 'Local'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Secure RPC Layer'),
        x509.NameAttribute(NameOID.COMMON_NAME, host)
    ])

    ip_address= ipaddress.ip_address(host)

    cert= (
        x509.CertificateBuilder()
        .issuer_name(issuer)
        .subject_name(subject)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days= 365))
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ip_address)]),
            critical= False
        )
        .sign(
            private_key,
            hashes.SHA256(),
            backend= default_backend()
        )
    )

    key_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'key.pem'))
    cert_file= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cert.pem'))

    with open(key_file, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding= serialization.Encoding.PEM,
                format= serialization.PrivateFormat.PKCS8,
                encryption_algorithm= serialization.BestAvailableEncryption(bytes(password, encoding='utf-8'))
            )
        )

    with open(cert_file, 'wb') as f:
        f.write(
            cert.public_bytes(
                encoding= serialization.Encoding.PEM
            )
        )


#generate_cert_and_private('127.0.0.1')
