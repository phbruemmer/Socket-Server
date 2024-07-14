import os
import socket
import time

import encryption

HOST_NAME = socket.gethostname()
HOST = socket.gethostbyname(HOST_NAME)
HOST = "127.0.0.1"
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
            def check_path(f):
                if os.path.exists(os.path.join(upload_dir, f)):
                    client_sock.sendall(b'$file-exists')
                    if check_rename_request():
                        rename_sequence()
                return f

            def rename_sequence():
                new_filename = client_sock.recv(BUFFER).decode()
                check_path(new_filename)

            def check_rename_request():
                rename_request = True
                request_data = client_sock.recv(BUFFER).decode()
                if request_data == "$n":
                    rename_request = False
                return rename_request

            upload_dir = "./uploaded_files/"
            file_name = client_sock.recv(BUFFER).decode()
            file_name = check_path(file_name)

            with open(os.path.join(upload_dir, file_name), 'wb') as file:
                _data = client_sock.recv(BUFFER)
                file.write(_data)
                while not _data.decode() == "$upload-finished":
                    _data = client_sock.recv(BUFFER)
                    print(_data.decode())
                    file.write(_data)
                    time.sleep(.1)

        def handle_download():
            uploaded_files = "./uploaded_files/"
            filename = client_sock.recv(BUFFER).decode()
            file_path = uploaded_files + filename
            time.sleep(.1)
            if os.path.exists(file_path):
                client_sock.sendall(str(os.path.getsize(file_path)).encode())
            else:
                client_sock.sendall("0".encode())
                return
            time.sleep(.1)
            with open(file_path, "rb") as file:
                file_chunk = file.read(1024)
                print(file_chunk.decode())
                client_sock.sendall(file_chunk)
                while not file_chunk.decode() == "":
                    print(file_chunk)
                    file_chunk = file.read(1024)
                    client_sock.sendall(file_chunk)
                    time.sleep(.1)
                client_sock.sendall("$download-finished".encode())

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
