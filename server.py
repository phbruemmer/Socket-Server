import os
import socket
import time

import encryption

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
HOST = "172.31.6.223"
PORT = 6544

BUFFER = 64000

print(HOST_NAME)
print(HOST)
print(PORT)

s = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)


def main():
    try:
        s.bind((HOST, PORT))
        print("Starting...")
    except Exception as err:
        print(err)
        exit(-1)

    s.listen(1)

    def accept():
        client_sock, client_addr = s.accept()
        loop(client_sock)

    def loop(client_sock):
        def handle_upload():
            upload_dir = "./uploaded_files/"
            time.sleep(.1)
            file_size = int(client_sock.recv(BUFFER).decode())
            chunks = file_size // 1024
            time.sleep(.1)
            file_name = client_sock.recv(BUFFER).decode()
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            with open(os.path.join(upload_dir, file_name), 'wb') as file:
                for i in range(0, chunks):
                    """
                    I should probably use a while-loop
                    and then check if I get data or not and
                    if not we just break the loop.
                    """
                    _data = client_sock.recv(BUFFER)
                    print(_data)
                    file.write(_data)
                    time.sleep(.1)

        def handle_download():
            pass

        def dirs():
            pass

        def helper():
            pass

        data = client_sock.recv(BUFFER)
        data = data.decode()
        decrypted_data = encryption.decrypt(data)
        print(decrypted_data)

        if decrypted_data == '$upload':
            handle_upload()
        elif decrypted_data == "$download":
            handle_download()
        elif decrypted_data == "$dirs":
            dirs()
        elif decrypted_data == "$help":
            helper()
        elif decrypted_data == "$exit":
            client_sock.shutdown(socket.SHUT_RDWR)
            client_sock.close()
            return
        else:
            client_sock.sendall(data.encode())
        loop(client_sock)

    accept()


if __name__ == '__main__':
    main()
