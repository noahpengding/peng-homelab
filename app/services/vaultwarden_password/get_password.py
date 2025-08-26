from app.utils.vaultwarden_client import BitwardenClient, BitwardenData


def get_password_by_name(name: str) -> BitwardenData:
    client = BitwardenClient()
    for cipher in client.get_ciphers("Share"):
        if cipher.name == name:
            return cipher
    return None


def get_passwords_by_url(url: str) -> list[BitwardenData]:
    client = BitwardenClient()
    results = []
    for cipher in client.get_ciphers("Share"):
        if cipher.url and url in cipher.url:
            results.append(cipher)
    return results


def get_password_by_name_and_username(name: str, username: str) -> BitwardenData:
    client = BitwardenClient()
    for cipher in client.get_ciphers("Share"):
        if cipher.name == name and cipher.username == username:
            return cipher
    return None
