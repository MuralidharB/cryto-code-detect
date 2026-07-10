from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def new_keypair():
    private_key = X25519PrivateKey.generate()
    return private_key, private_key.public_key()


def shared_secret(my_private, their_public) -> bytes:
    return my_private.exchange(their_public)


if __name__ == "__main__":
    alice_priv, alice_pub = new_keypair()
    bob_priv, bob_pub = new_keypair()
    s1 = shared_secret(alice_priv, bob_pub)
    s2 = shared_secret(bob_priv, alice_pub)
    print(s1 == s2)
