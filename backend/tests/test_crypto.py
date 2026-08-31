from app.security.crypto import decrypt_secret, encrypt_secret, key_last4


def test_encrypt_decrypt_roundtrip():
    secret = "sk-test-openai-key-abc123"
    blob = encrypt_secret(secret)
    assert blob != secret.encode()
    assert decrypt_secret(blob) == secret


def test_key_last4():
    assert key_last4("sk-abcdefgh") == "efgh"
