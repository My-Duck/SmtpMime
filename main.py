import argparse
import os
import socket
import getpass
import smtp_api
import mail_generator


def parse_args():
    arg_parser = argparse.ArgumentParser('python main.py')
    arg_parser.add_argument('-s', '--server', required=True, type=get_server,
                            help='Server address in format address[:port] (default port is 25)')
    arg_parser.add_argument('-t', '--to', required=True, help='Recipient e-mail address')
    arg_parser.add_argument('-f', '--from', metavar='_from', default='<>', help='Sender\'s e-mail address (default is <>)')
    arg_parser.add_argument('--subject', default='Happy Pictures', help='Letter subject (default is "Happy Pictures")')
    arg_parser.add_argument('--auth', action='store_true', help='Use authentification')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Use verbose mode')
    arg_parser.add_argument('-d', '--directory', default=os.getcwd(), help='Directory with images (default is $pwd)')
    arg_parser.add_argument('-ssl', action='store_true', help='Use ssl')
    arg_parser.add_argument('-p', '--pipeline', action='store_true', help='Use pipelining (if server supports it)')
    res = arg_parser.parse_args()
    if res.auth:
        login, password = auth()
        return res, (login, password)
    return res,


def get_server(raw_server):
    tmp = raw_server.split(':')
    if len(tmp) == 1:
        server = tmp[0]
        socket.gethostbyname(server)
        port = 25
    else:
        server = tmp[0]
        socket.gethostbyname(server)
        port = int(tmp[1])
        if not (0 <= port <= 65535):
            raise argparse.ArgumentTypeError
    return server, port


def auth():
    print('Login:', end=' ')
    login = input()
    password = getpass.getpass()
    return login, password


def generate_mail(_from, _to, subject, directory):
    mail_gen = mail_generator.MailGenerator(_from, _to, subject)
    images = mail_generator.MailGenerator.find_images(directory)
    for image in images:
        mail_gen.add_image_to_attachment(image)
    return mail_gen.create_mail()


if __name__ == '__main__':
    res = parse_args()
    args = res[0]
    print(args.server, args.verbose, args.ssl)
    smtp_socket = smtp_api.SmtpApi(*args.server, args.verbose)
    smtp_socket.start_connection(args.ssl)
    if args.auth:
        smtp_socket.auth(*res[1])

    mail = generate_mail(args.__getattribute__('from'), args.to, args.subject, args.directory)
    if args.pipeline and smtp_socket.pipelining:
        smtp_socket.send_mail_pipeline(args.__getattribute__('from'), args.to, mail)
    else:
        smtp_socket.send_mail(args.__getattribute__('from'), args.to, mail)
    smtp_socket.close_connection()

