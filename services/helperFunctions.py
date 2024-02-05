import random
import string
import re
import json
import hashlib


def generate_order_number():
    # Create parts of the order number using random choices
    num1 = str(random.randint(0, 9))
    letter1 = random.choice(string.ascii_uppercase)
    letter2 = random.choice(string.ascii_uppercase)
    num2 = str(random.randint(0, 9))
    letter3 = random.choice(string.ascii_uppercase)
    letter4 = random.choice(string.ascii_uppercase)

    # Combine parts to get the order number
    order_number = num1 + letter1 + letter2 + num2 + letter3 + letter4

    return order_number


def remove_special_characters(input_str):
    # Using regular expressions, we replace any character that is NOT an alphanumeric character
    # or a space with nothing (i.e., remove it).
    return re.sub(r'[^a-zA-Z0-9\s]', '', input_str)



def hash_dict(d):
    serialized_data = json.dumps(d, sort_keys=True).encode('utf-8')
    return hashlib.sha256(serialized_data).hexdigest()