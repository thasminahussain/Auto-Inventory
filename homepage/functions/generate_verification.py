import secrets
import string

def generate_verification_token(length=32):
    """
    Generate a random verification token.

    Args:
        length (int): Length of the token (default is 32).

    Returns:
        str: Random verification token.
    """

    characters = string.ascii_letters + string.digits

    token = ''.join(secrets.choice(characters) for _ in range(length))
    
    return token