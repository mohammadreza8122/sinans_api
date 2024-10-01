import random
import uuid
import os


def rename_product_file(instance,filename):
    path = 'products'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_banners_file(instance,filename):
    path = 'banners'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_sliders_file(instance,filename):
    path = 'sliders'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_file(instance,filename):
    path = str(instance)
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)


def rename_document_file(instance,filename):
    path = 'document/'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_article_file(instance,filename):
    path = 'articles/banners'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_images_file(instance,filename):
    path = 'images'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_popup_file(instance,filename):
    path = 'popups/banners'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)
    
def rename_product_catalogue_file(instance,filename):
    path = 'products/catalogues'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

def rename_profile_image(instance,filename):
    path = 'profile/image'
    ext = filename.split('.')[-1]
    filename = "{}.{}".format(uuid.uuid4(),ext)
    return os.path.join(path, filename)

    