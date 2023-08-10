import re

def usernameValidator(username: str):
    regex: str = r"^[\w.@+-]{1,149}$"
    if re.fullmatch(regex, username) is None:
        return False
    return True


def emailValidator(email: str):
    regex: str = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.fullmatch(regex, email) is None:
        return False
    return True


def passwordValidator(password: str):
    notNumericRegex: str = r"^.*\D.*$"
    if (
        len(password) >= 8
        and (re.fullmatch(notNumericRegex, password) is not None)
    ):
        return True
    return False


def confirmPassword(username: str, password: str, password2: str):
    if password2 and passwordValidator(username, password2) and (password == password2):
        return True
    return False
