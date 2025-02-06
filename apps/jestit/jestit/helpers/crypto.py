from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json

def encrypt(data, key):
    if isinstance(data, dict):
        data = json.dumps(data)
    if not isinstance(data, str):
        raise ValueError("Data must be a string or a dictionary")

    data = data.encode('utf-8')

    # Create a new AES cipher with the key and a random IV
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC)
    iv = cipher.iv

    # Pad the data to make it a multiple of the AES block size
    padded_data = pad(data, AES.block_size)

    # Encrypt the padded data
    encrypted_data = cipher.encrypt(padded_data)

    # Encode the IV and encrypted data as Base64 and concatenate them
    encrypted_data_b64 = b64encode(iv + encrypted_data).decode('utf-8')

    return encrypted_data_b64

def decrypt(enc_data_b64, key):
    # Decode the base64 data to retrieve the bytes
    enc_data_bytes = b64decode(enc_data_b64)

    # Extract the IV and the encrypted data
    iv = enc_data_bytes[:AES.block_size]
    encrypted_data = enc_data_bytes[AES.block_size:]

    # Create a new AES cipher with the key and the extracted IV
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)

    # Decrypt the data
    decrypted_padded_data = cipher.decrypt(encrypted_data)

    # Unpad the decrypted data
    decrypted_data = unpad(decrypted_padded_data, AES.block_size)

    # Try to decode the decrypted data as UTF-8
    try:
        decrypted_data_str = decrypted_data.decode('utf-8')
        return json.loads(decrypted_data_str)
    except json.JSONDecodeError:
        return decrypted_data_str
