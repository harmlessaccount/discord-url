import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_digits(length=10):
    return ''.join(random.choices(string.digits, k=length))

def anonymizer(jsonData):
    if isinstance(jsonData, dict):
        anonymized = {}
        for key, value in jsonData.items():
            if key in ['id', 'phone']:
                anonymized[key] = random_digits(len(str(value)))  # Anonymize IDs and phone numbers
            elif key == 'discriminator':
                anonymized[key] = random_digits(len(str(value)))  # Anonymize usernames
            elif key in ['username', 'global_name']:
                anonymized[key] = random_string()
            elif key == 'email':
                anonymized[key] = random_string(8) + '@harmless.com'  # Anonymize email
            elif key == 'name':
                anonymized[key] = "Harmless Guild"  # Anonymize guild names to a fixed value
            elif key in ['icon', 'banner']:
                anonymized[key] = ''.join(random.choices('abcdef' + string.digits, k=32))  # Anonymize icons and banners
            elif key in 'locale': 
                anonymized[key] = "en-US" # Anonymize locale
            else:
                anonymized[key] = value
        return anonymized
    elif isinstance(jsonData, list):
        return [anonymizer(item) for item in jsonData]
    else:
        return jsonData
