import random, string


def random_key(length):
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
    key = ''.join(random.choice(alphabet) for _ in range(length))
    return key
    