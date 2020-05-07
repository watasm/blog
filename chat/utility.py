from uuid import uuid4

def encrypt_image_name(instance, filename):
    extension = filename.split('.')[-1]
    return 'chat/images/{}.{}'.format(uuid4().hex, extension)
