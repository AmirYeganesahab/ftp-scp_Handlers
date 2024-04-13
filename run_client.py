import argparse
from ftplib import FTP_TLS
import ssl
import concurrent.futures
import os


class FTPClient:
    def __init__(self, server, user, pwd, certfile, keyfile):
        # Define the context for the secure connection
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Do not verify the server's certificate
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)

        self.ftps = FTP_TLS(context=context)
        self.ftps.set_debuglevel(2)  # print all interactions with the server

        print("Connecting...")
        response = self.ftps.connect(host=server, port=8090)
        print("Response:", response)

        print("Logging in...")
        response = self.ftps.login(user=user, passwd=pwd)
        print("Response:", response)

        print("Switching to secure data connection...")
        response = self.ftps.prot_p()
        print("Response:", response)

        print("Setting to active mode...")
        self.ftps.set_pasv(False)

        print("Getting current directory...")
        response = self.ftps.sendcmd("PWD")
        print("Response:", response)

        self.transferred_files = self.load_transferred_files()

    def load_transferred_files(self):
        if os.path.exists("transferred_files.txt"):
            with open("transferred_files.txt", "r") as f:
                return set(line.strip() for line in f)
        else:
            return set()

    def save_transferred_file(self, filename):
        with open("transferred_files.txt", "a") as f:
            f.write(filename + "\n")
        self.transferred_files.add(filename)

    def upload_file(self, src, dst):
        if src in self.transferred_files:
            print("File already transferred, skipping...")
            return
        print("Uploading file...")
        try:
            with open(src, "rb") as file:
                response = self.ftps.storbinary("STOR " + dst, file)
            print("Response:", response)
            self.save_transferred_file(src)
        except Exception as e:
            print("____________________________________")
            print("Exception:", e)

    def upload_files(self, files):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.upload_file, src, dst) for src, dst in files
            ]
            for future in concurrent.futures.as_completed(futures):
                print("Response:", future.result())

    def close(self):
        self.ftps.quit()


if __name__ == "__main__":
    # python script.py --server SERVER_ADRESS --user USER --pwd PASSWORD --certfile path/to/cert.pem --keyfile path/to/key.pem
    parser = argparse.ArgumentParser(description="FTP client")
    parser.add_argument("--server", required=True, help="Server IP address")
    parser.add_argument("--user", required=True, help="Username")
    parser.add_argument("--pwd", required=True, help="Password")
    parser.add_argument("--certfile", required=True, help="Path to certificate file")
    parser.add_argument("--keyfile", required=True, help="Path to key file")
    args = parser.parse_args()

    client = FTPClient(args.server, args.user, args.pwd, args.certfile, args.keyfile)

    import pathlib

    p = pathlib.Path("/home/ibex/Documents/test_data/N840")
    files = [(str(file), file.name) for file in p.glob("*.png")]
    print(files)
    [client.upload_file(src, dst) for src, dst in files]
    # client.upload_files(files)

    # client.upload_file('/home/ibex/Documents/ftp_dir/test.txt', 'test222.txt')
    # client.close()
