#!/usr/bin/env python

from Crypto.Cipher import AES
import hashlib

def pad(data):
	length = 16 - (len(data) % 16)
	data += chr(length)*length
	return data

# def encrypt(plainText,workingKey):
#     iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'.encode('utf-8') 
#     plainText = pad(plainText)
#     encDigest = hashlib.md5()
#     encDigest.update(workingKey.encode('utf-8') )
#     enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
#     # print(f"Updated => Yes")
#     encryptedText = enc_cipher.encrypt(plainText).encode('hex')
#     return encryptedText

def encrypt(plainText, workingKey):
    try:

        key1 = str.encode(workingKey)

        # iv = Random.new().read(AES.block_size)
        iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'.encode('utf-8') 

        obj = AES.new(key1, AES.MODE_CBC, iv)
        encrypted = obj.encrypt(str.encode(plainText))
        print(encrypted)
        # return encrypted

    except Exception as e:
        print(e)
        print("Error Occured")
        return 'Error'



def decrypt(cipherText,workingKey):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = hashlib.md5()
    decDigest.update(workingKey)
    encryptedText = cipherText.decode('hex')
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    decryptedText = dec_cipher.decrypt(encryptedText)
    return decryptedText
