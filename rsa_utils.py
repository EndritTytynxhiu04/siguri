from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes



def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    return private_key, public_key


def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def load_public_key(public_key_pem):
    return serialization.load_pem_public_key(public_key_pem)


def load_private_key(private_key_pem):
    return serialization.load_pem_private_key(
        private_key_pem,
        password=None
    )


def encrypt_aes_key(aes_key, receiver_public_key):
    encrypted_aes_key = receiver_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_aes_key


def decrypt_aes_key(encrypted_aes_key, receiver_private_key):
    aes_key = receiver_private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return aes_key


def sign_data(data, sender_private_key):
    signature = sender_private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature


def verify_signature(data, signature, sender_public_key):
    try:
        sender_public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True

    except Exception:
        return False


def sign_hash(hash_value, sender_private_key):
    if isinstance(hash_value, str):
        hash_value = hash_value.encode("utf-8")

    return sign_data(hash_value, sender_private_key)


def verify_hash_signature(hash_value, signature, sender_public_key):
    if isinstance(hash_value, str):
        hash_value = hash_value.encode("utf-8")

    return verify_signature(hash_value, signature, sender_public_key)