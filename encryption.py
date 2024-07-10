from random import randint
from string import digits, punctuation, ascii_letters

valid_key = digits + punctuation + ascii_letters


def encrypt_data(data, k128):
    def key128():
        key_ = ""
        for i in range(0, 128):
            key_ += valid_key[randint(0, len(valid_key) - 1)]
        return key_

    def key512():
        key_ = ""
        for i in range(0, 512):
            key_ += valid_key[randint(0, len(valid_key))]
        return key_

    if k128:
        size = 128
        key_ = key128()
    else:
        size = 512
        key_ = key512()
    key_counter = 0
    encrypted_ = ""

    for i in range(0, len(data)):
        if key_counter == 128:
            key_counter = 0
        encrypted_ += chr(ord(data[i]) + ord(key_[key_counter]))
        key_counter += 1
    encrypted_ = key_ + encrypted_ + str(size)
    return encrypted_


def decrypt(data):
    key_size = data[-3] + data[-2] + data[-1]
    key_ = ""
    decrypted_ = ""
    key_counter = 0

    for i in range(0, int(key_size)):
        key_ += data[i]
    data = data[int(key_size):]
    data = data[:-len(key_size)]

    for i in range(0, len(data)):
        if key_counter == 128:
            key_counter = 0
        decrypted_ += chr(abs(ord(key_[key_counter]) - ord(data[i])))
        key_counter += 1
    return decrypted_


if __name__ == "__main__":
    encrypted = encrypt_data("Test Nachricht -> <-", True)
    print(encrypted)
    decrypted = decrypt(encrypted)
    print(decrypted)
