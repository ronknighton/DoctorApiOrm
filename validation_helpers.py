import re
from validate_email import validate_email
import uuid
import hashlib


def is_npi_good(code):
    if code is None:
        return False
    if len(code) != 10 or not code.isdigit():
        return False
    else:
        return True


def is_postal_code_good(code):
    if code is None:
        return False
    if len(code) != 5 or not code.isdigit():
        return False
    else:
        return True


def is_radius_good(radius):
    if radius is None:
        return False
    if not radius.isdigit() or int(radius) > 50:
        return False
    else:
        return True


def is_taxonomy_good(tax):
    if tax is None:
        return False
    if len(tax) != 10:
        return False
    if tax != '':
        first_three = tax[:3]
        last_three = tax[-4:-1]
        # three = int(last_three)
        # print(three)
        if not first_three.isdigit():
            return False
        elif not last_three.isdigit():
            return False
        else:
            return True


def is_string_good(word, length=35):
    if word is None:
        return False
    if len(word) > length:
        return False
    elif not re.match(r'^\w+$', word):
        return False
    else:
        return True


def is_phrase_good(phrase, length=35):
    if phrase is None:
        return False
    if len(phrase) > length:
        return False
    phrase_list = phrase.split(' ')
    for word in phrase_list:
        if not is_string_good(word):
            return False
    return True


def is_comment_good(comment):
    if comment is None:
        return False
    if comment != '':
        length = len(comment)
        if length > 455:
            return False
        words = comment.split(' ')
        for line in words:
            line = line.replace(',', '')
            line = line.replace('.', '')
            line = line.replace('!', '')
            if not re.match(r'^\w+$', line):
                return False
    return True


def filter_message(message, length=50):
    message = message[:length]
    filtered = ""
    for line in message.split('\n'):
        line = re.sub(r"[^a-zA-Z0-9]+", ' ', line)
        filtered += line + '\n'
    return filtered


def check_email(email):
    if email is None:
        return False
    return validate_email(email)


def validate_password(password, length=15):
    if len(password) > length:
        return False
    spaces = re.findall(' ', password)
    if len(spaces) > 0:
        return False
    else:
        return True


def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def is_uuid_good(code):
    if code is None or code == '':
        return False
    code_list = code.split('-')
    if len(code_list) != 5:
        return False
    else:
        return True


def is_user_allowed_post_comment(user, now, time_span):
    if not user['Verified']:
        return False
    if not user['LoggedIn']:
        return False
    login_time = user['LoginTime']
    elapsed_time = now - login_time
    # Allows 1 hour for posting/editing/deleting comments
    hours = elapsed_time.seconds / 3600
    if hours > time_span:
        return False
    return True



