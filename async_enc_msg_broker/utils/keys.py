from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone, timedelta
import os 
from dotenv import load_dotenv, get_key
import ipaddress


env_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(env_path)



def generate_password():
    key= Fernet.generate_key()

    with open(env_path, 'wb') as f:
        f.write(f"PASSWORD={key.decode('utf-8')}".encode('utf-8'))

#generate_password()
#password= get_key(dotenv_path=env_path, key_to_get='PASSWORD')
password= os.environ.get('PASSWORD')
password_bytes= bytes(password, encoding='utf-8')


def generate_cert_and_key(host_ip:str):
    global password_bytes

    private_key= rsa.generate_private_key(
        public_exponent= 65537,
        key_size= 2048
    )

    subject= issuer= x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'AE'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'Localhost'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, 'Local'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Secure socket layer'),
        x509.NameAttribute(NameOID.COMMON_NAME, host_ip)
    ])

    ip_address= ipaddress.ip_address(host_ip)

    cert=(
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days= 365))
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ip_address)]),
            critical=False
        )
        .sign(
            private_key,
            hashes.SHA256(),
            default_backend()
        )
    )

    cert_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cert.pem'))
    key_path= os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'key.pem'))

    with open(key_path, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding= serialization.Encoding.PEM,
                format= serialization.PrivateFormat.PKCS8,
                encryption_algorithm= serialization.BestAvailableEncryption(password_bytes)
            )
        )

    with open(cert_path, 'wb') as f:
        f.write(
            cert.public_bytes(
                encoding= serialization.Encoding.PEM
            )
        )

'''
if __name__ == "__main__":
    generate_cert_and_key('127.0.0.1')

'''



