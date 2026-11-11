#!/usr/bin/env python3
import datetime, json, os, urllib.request

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

IMP = "data/imp.json"
AAA = "data/aaa_root.pem"
IMP_URL = "https://emudhra.we-have-a-problem.com/impacted-intermediates.json"
AAA_URL = "http://crt.comodoca.com/AAACertificateServices.crt"
OUT = "certs"
DOMAIN = "townak.benesse.ne.jp"
ISSUER = "EM DV TLS CA - G3B"
D = 156

def ensure_data():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(IMP):
        urllib.request.urlretrieve(IMP_URL, IMP)
    if not os.path.exists(AAA):
        raw = urllib.request.urlopen(AAA_URL, timeout=30).read()
        cert = x509.load_der_x509_certificate(raw)
        open(AAA, "wb").write(cert.public_bytes(serialization.Encoding.PEM))

def main():
    ensure_data()
    data = json.load(open(IMP))
    e = [x for x in data if ISSUER in x["name"] and "AAA Certificate Services" in x.get("issuer", "")][0]
    inter = x509.load_pem_x509_certificate(e["pem"].encode())
    ca_key = ec.derive_private_key(D, ec.SECP384R1())
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, DOMAIN)]))
        .issuer_name(inter.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(inter.not_valid_after)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(DOMAIN)]), critical=False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(ca_key, hashes.SHA384())
    )
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "leaf.key"), "wb").write(
        key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption())
    )
    open(os.path.join(OUT, "fullchain.pem"), "wb").write(
        cert.public_bytes(serialization.Encoding.PEM) + e["pem"].strip().encode() + b"\n" + open(AAA, "rb").read()
    )

if __name__ == "__main__":
    main()
