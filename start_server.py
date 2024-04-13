import argparse
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer


def main(args):
    # Instantiate a dummy authorizer to manage 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions
    authorizer.add_user(args.username, args.password, args.ftp_dir, perm="elradfmwM")

    # Instantiate FTP handler class
    handler = TLS_FTPHandler
    handler.authorizer = authorizer
    # handler.passive_ports = range(60000, 65535)
    # Specify the SSL certificate and key files
    handler.certfile = args.certfile
    handler.keyfile = args.keyfile

    # Define a new FTP server on the default address (127.0.0.1) and port (2121)
    server = FTPServer((args.server_ip, args.server_port), handler)
    # server.passive_ports = range(8050, 8100)
    # Start the FTP server
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start an FTP server.")
    parser.add_argument("--username", required=True, help="FTP username")
    parser.add_argument("--password", required=True, help="FTP password")
    parser.add_argument("--ftp_dir", required=True, help="FTP directory")
    parser.add_argument(
        "--certfile", required=True, help="Path to SSL certificate file"
    )
    parser.add_argument("--keyfile", required=True, help="Path to SSL key file")
    parser.add_argument("--server_ip", default="127.0.0.1", help="Server IP address")
    parser.add_argument("--server_port", type=int, default=2121, help="Server port")
    args = parser.parse_args()
    main(args)

    # python start_server.py --username USER --password PASS --ftp_dir path/to/files --certfile path/to/cert.pem --keyfile path/to/files/key.pem --server_ip 192.168.1.106 --server_port 8090
