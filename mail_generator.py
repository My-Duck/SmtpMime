import base64
import os
import sys
import ssl


class MailGenerator:
    IMAGES_EXTENSIONS = ['.jpg', '.png', '.jpeg']

    def __init__(self, _from, to, subject):
        self.attachments = []

        self.from_header = b'From: <' + _from.encode() + b'>'
        self.to_header = b'To: <' + to.encode() + b'>'
        self.subject_header = b'Subject: =?utf-8?B?' + base64.b64encode(subject.encode()) + b'?='
        self.content_header = b'Content-Type: multipart/mixed; boundary='

    def chose_boundary(self):
        boundary = ssl.RAND_bytes(10)
        while True:
            flag = False
            for attachment in self.attachments:
                if attachment.find(boundary) != -1:
                    flag = True
                    break
            if flag:
                boundary = ssl.RAND_bytes(10)
            else:
                break
        return boundary

    def create_mail(self):
        self.boundary = self.chose_boundary()
        middle_boundary = b'\r\n--' + self.boundary + b'\r\n'
        end_boundary = b'\r\n--' + self.boundary + b'--'
        self.content_header += self.boundary

        headers = b'\r\n'.join((self.from_header, self.to_header, self.subject_header, self.content_header)) + b'\r\n'

        data = middle_boundary + middle_boundary.join(self.attachments) + end_boundary
        return headers + data

    def add_image_to_attachment(self, image):
        with open(image, 'rb') as f:
            image_data = f.read()
        coded_data = base64.b64encode(image_data)

        _, file_extension = os.path.splitext(image)
        filename = os.path.basename(image)

        if file_extension == '.jpeg' or file_extension == '.jpg':
            content_type = b'image/jpg;'
        elif file_extension == '.png':
            content_type = b'image/png;'
        content_type_header = b'Content-Type: ' + content_type
        content_disposition_header = b'Content-Disposition: attachment; filename="' + filename.encode() + b'"'
        content_encoding_header = b'Content-Transfer-Encoding: base64'
        data = b'\r\n'.join((content_type_header, content_disposition_header, content_encoding_header, b'\r\n', coded_data)) + b'\r\n'
        self.attachments.append(data)

    @staticmethod
    def find_images(path):
        _images = []
        try:
            for file in os.listdir(path):
                for ext in MailGenerator.IMAGES_EXTENSIONS:
                    if file.endswith(ext):
                        _images.append(os.path.join(path, file))
        except OSError:
            print(f'Wrong directory {path}')
            sys.exit(1)
        return _images

