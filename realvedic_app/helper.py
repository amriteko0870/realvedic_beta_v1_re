# ---------------- Keys ------------------------------------------
# accessCode = 'AVLA04KF94AB88ALBA' # localhost:8080
# workingKey = 'F67B32AF1FDF264315E2CD3254D28030'  # localhost:8080
accessCode = 'AVFO04KE94CN66OFNC' # andaal 	
workingKey = 'DE16C051DB632BEA851E1F882B8BCDD5' # andaal

# ----------------  utils ------------------------------------------
from Crypto.Cipher import AES
import hashlib

def pad(data):
	length = 16 - (len(data) % 16)
	data += chr(length)*length
	return data
def encrypt(plainText,workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plainText = pad(plainText)
    encDigest = hashlib.md5()
    encDigest.update(workingKey.encode())
    enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
    encryptedText = enc_cipher.encrypt(plainText.encode()).hex()
    return encryptedText
def decrypt(cipherText,workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    decDigest = hashlib.md5()
    decDigest.update(workingKey.encode())
    encryptedText = bytes.fromhex(cipherText)
    dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
    decryptedText = dec_cipher.decrypt(encryptedText)
    return str(decryptedText)


# ----------- response handler ----------------------------------------------
from string import Template

def res(encResp): 
    '''
    Please put in the 32 bit alphanumeric key in quotes provided by CCAvenues.
    '''
    data = decrypt(encResp,workingKey)
    data = data[2:-1]
    data = data.split('&')
    res_data = {}
    for i in data:
        row = i.split('=')
        res_data[row[0]] = str(row[1])
    return res_data

# ------------------------ Link Creation -----------------------------------------------

def link_creation(p_merchant_id,p_order_id,p_currency,p_amount,p_redirect_url,p_cancel_url,p_language,p_billing_name,p_billing_address,p_billing_city,p_billing_state,p_billing_zip,p_billing_country,p_billing_tel,p_billing_email,merchant_param1):
    # p_merchant_id = "2336508"
    # p_order_id = 'Test1234'
    # p_currency = 'INR'
    # p_amount = '1.00'
    # p_redirect_url = 'http://localhost:8001/payment_success'
    # p_cancel_url = 'http://localhost:8001/payment_cancel'
    # p_language = 'EN'
    # p_billing_name = 'Amrit'
    # p_billing_address = 'Test address'
    # p_billing_city = 'Bangalore'
    # p_billing_state = 'KA'
    # p_billing_zip = '560029'
    # p_billing_country = 'India'
    # p_billing_tel = '919988776655'
    # p_billing_email = 'demo@demo.com'
    # merchant_param1 = '1'

    merchant_data = 'merchant_id='+p_merchant_id+\
                    '&'+'order_id='+p_order_id+\
                    '&'+"currency="+p_currency+\
                    '&'+'amount='+p_amount+\
                    '&'+'redirect_url='+p_redirect_url+\
                    '&'+'cancel_url='+p_cancel_url+\
                    '&'+'language='+p_language+\
                    '&'+'billing_name='+p_billing_name+\
                    '&'+'billing_address='+p_billing_address+\
                    '&'+'billing_city='+p_billing_city+\
                    '&'+'billing_state='+p_billing_state+\
                    '&'+'billing_zip='+p_billing_zip+\
                    '&'+'billing_country='+p_billing_country+\
                    '&'+'billing_tel='+p_billing_tel+\
                    '&'+'billing_email='+p_billing_email+\
                    '&'+'merchant_param1='+merchant_param1

    encryption = encrypt(merchant_data,workingKey)

    link = f"https://test.ccavenue.com/transaction/transaction.do?command=initiateTransaction&merchant_id={p_merchant_id}&encRequest={encryption}&access_code={accessCode}"
    return link