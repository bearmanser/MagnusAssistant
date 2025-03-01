import os
import subprocess
import socket
import ipaddress
import time
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta

from flask.cli import load_dotenv

from config.config import get_config_value
from text_to_speech.run_piper import run_piper
from twilio_socket.twilio import start_twilio

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import threading
from endpoints.Endpoints import start_flask
from frontend.run_web import start_npm
from websocket.websocket_handler import start_websocket_server


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def main():
    load_dotenv()

    if not is_port_in_use(3000):
        host_ip = get_host_ip()
        ip_address = ipaddress.ip_address(host_ip)
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
                x509.NameAttribute(NameOID.COMMON_NAME, host_ip),
            ]
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([x509.IPAddress(ip_address)]),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )
        with open(os.path.join("./frontend", "key.pem"), "wb") as private_key_file:
            private_key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(os.path.join("./frontend", "cert.pem"), "wb") as cert_file:
            cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

        if os.name != "nt":  # Only run this on non-Windows systems
            archive_path = "text_to_speech/piper_linux/piper_linux_x86_64.tar.gz"
            extract_path = "text_to_speech/piper_linux"

            # Check if the extracted files already exist to avoid unnecessary extraction
            if not os.path.exists(os.path.join(extract_path, "piper")):
                try:
                    print("Extracting piper_linux_x86_64.tar.gz...")
                    subprocess.run(
                        ["tar", "-xzf", archive_path, "-C", extract_path], check=True
                    )
                    print("Extraction complete.")
                except subprocess.CalledProcessError as e:
                    print(f"Error during extraction: {e}")

        npm_thread = threading.Thread(target=start_npm)
        npm_thread.start()

    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    websocket_thread = threading.Thread(target=start_websocket_server)
    websocket_thread.start()

    twilio_thread = threading.Thread(target=start_twilio)
    twilio_thread.start()

    while True:
        time.sleep(1) 


if __name__ == "__main__":
    main()
