import argparse
import os
import paramiko
import concurrent.futures

from scp import SCPClient


class SCPClientWrapper:
    def __init__(self, server, user, pwd, keyfile, dest):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(server, username=user, password=pwd, key_filename=keyfile)
        self.scp = SCPClient(self.ssh.get_transport())
        self.transferred_files = self.load_transferred_files()
        self.dest = dest

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
            self.scp.put(src, dst)
            print("File transferred successfully")
            self.save_transferred_file(src)
        except Exception as e:
            print("Exception:", e)

    def upload_files(self, files):
        for src, dst in files:
            dst = os.path.join(self.dest, dst)
            self.upload_file(src, dst)

    # def upload_files(self, files):
    #     with concurrent.futures.ThreadPoolExecutor() as executor:
    #         futures = [executor.submit(self.upload_file, src, os.path.join(self.dest, dst)) for src, dst in files]
    #         for future in concurrent.futures.as_completed(futures):
    #             print('Result:', future.result())

    def close(self):
        self.scp.close()
        self.ssh.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCP client")
    parser.add_argument("--server", required=True, help="Server IP address")
    parser.add_argument("--user", required=True, help="Username")
    parser.add_argument("--pwd", required=True, help="Password")
    parser.add_argument("--keyfile", required=True, help="Path to key file")
    parser.add_argument("--dest", required=True, help="Path to transfer on server")
    args = parser.parse_args()

    client = SCPClientWrapper(args.server, args.user, args.pwd, args.keyfile, args.dest)
    import pathlib

    p = pathlib.Path("/home/ibex/Documents/test_data/N840")
    files = [(str(file), file.name) for file in p.glob("*.png")]
    print(files)
    client.upload_files(files)
    # client.close()
