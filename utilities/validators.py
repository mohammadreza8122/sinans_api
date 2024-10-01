import os
from django.core.exceptions import ValidationError
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.zip']
    if not ext.lower() in valid_extensions:
        raise ValidationError('پسوند فایل اشتباه است')


def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 1.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("حداکثر سایز عکس %sMB" % str(megabyte_limit))