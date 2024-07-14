import socket
import time
import os
import encryption

host_name = socket.gethostname()
host = socket.gethostbyname(host_name)

server_ip = "127.0.0.1"

port = 6544

print(host_name)
print(host)
print(port)

BUFFER = 1024

s = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
    proto=0
)


def main():
    try:
        s.connect((server_ip, port))
        print(f"Successfully connected to the Server. ({server_ip}:{port})")
    except:
        print("Something went wrong.\nTry to contact the server host. (Probably the Server is not online.)")
        exit(-1)

    chat()


def file_uploader():
    def rename_serverside_file():
        print("# # #\nF I L E - A L R E A D Y - E X I S T S\n# # #\n")
        rename = input("Do you want to rename your file for the upload? (y/n)")
        if rename == "n":
            s.send("$n".encode())
            return None
        s.send("$y".encode())
        new_filename_ = input("(filename) > ")
        while not check_serverside_files(new_filename_):
            rename_serverside_file()
            break
        return new_filename_

    def check_serverside_files(f):
        file_available = True
        s.send(f.encode())
        check = s.recv(BUFFER).decode()
        if check == "$file-exists":
            file_available = False
        return file_available

    print("# # # # # # #\nE N T E R - P A T H\n# # # # # # #\n")
    path = input("(path) > ")

    if not os.path.exists(path):
        print("# # #\nP A T H - D O E S - N O T - E X I S T\n# # #")
        return

    s.send(encryption.encrypt_data('$upload', True).encode())
    file_name = os.path.basename(path)

    if not check_serverside_files(file_name):
        new_filename = rename_serverside_file()
        if new_filename is None:
            return

    with open(path, 'rb') as file:
        file_chunk = file.read(BUFFER)
        s.send(file_chunk)
        while file_chunk:
            print(file_chunk)
            file_chunk = file.read(BUFFER)
            s.send(file_chunk)
            print(file_chunk)
            time.sleep(.1)
        s.send("$upload-finished".encode())
        print("# F I L E - N O T - F O U N D #")


def file_downloader():
    download_dir = "./downloaded_files/"

    def check_filename(f):
        valid_file_ = False
        s.send(f.encode())
        time.sleep(.1)
        validation = s.recv(BUFFER).decode()
        if int(validation) > 0:
            valid_file_ = True
        return valid_file_

    def check_download_space(f):
        valid_space = False
        if os.path.exists(os.path.join(download_dir, f)):
            valid_space = True
        return valid_space

    def rename_file():
        print("# # #\nF I L E N A M E - N O T - A V A I L A B L E\n# # #")
        rename = input("Do you want to rename your local file? (y/n)")
        if rename == "n":
            return False
        print("# # #\nR E N A M E - F I L E\n# # #")
        new_file_name = input("(filename) > ")
        if check_download_space(new_file_name):
            rename_file()
        return new_file_name

    print("# # # # # # #\nF I L E N A M E\n# # # # # # #\n")
    filename = input("(filename) > ")
    download_file = filename
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    check = check_download_space(filename)
    print(check)
    if check:
        valid_file = rename_file()
        print(valid_file)
        if not valid_file:
            print(">>> Stopping download process...\n")
            return
        else:
            filename = valid_file
    s.send(encryption.encrypt_data('$download', True).encode())
    if not check_filename(download_file):
        print("# # #\nN O - S U C H - F I L E - F O U N D\n# # #")
        return
    with open(os.path.join(download_dir, filename), "wb") as file:
        file_data = s.recv(BUFFER)
        print(file_data.decode())
        while not file_data.decode() == "$download-finished":
            file.write(file_data)
            file_data = s.recv(BUFFER)
            print(file_data.decode())
            time.sleep(.1)


def chat():
    msg = input("> ")

    if msg == "$exit":
        msg = encryption.encrypt_data("$exit", True)
        s.send(msg.encode())
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return

    if msg == "$upload":
        file_uploader()
    elif msg == "$download":
        file_downloader()
    else:
        send(msg)
    chat()


def send(msg):
    msg = encryption.encrypt_data(msg, True)
    s.send(msg.encode())
    time.sleep(.1)
    recv()


def recv():
    msg = s.recv(BUFFER)
    msg = msg.decode()
    print(msg)
    msg = encryption.decrypt(msg)
    print(msg)


if __name__ == '__main__':
    main()
