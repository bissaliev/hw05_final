import io
import os
import sys

from django.core.files.base import ContentFile, File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image


class WEBPFieldFile(ImageFieldFile):
    """
    Класс наследник от ImageFieldFile, который производит
    сохранение файла с автоматической конвертацией в WEBP формат.
    """

    def save(self, name, content, save=True):
        content.file.seek(0)
        image = Image.open(content.file)
        image_bytes = io.BytesIO()
        image.save(fp=image_bytes, format="WEBP")
        name = f"{os.path.splitext(name)[0]}.webp"
        image_content_file = ContentFile(content=image_bytes.getvalue())
        super().save(name, image_content_file, save)


class WEBPField(models.ImageField):
    """
    Класс наследник от ImageField,
    который использует WEBPFieldFile вместо ImageFieldFile.
    """

    attr_class = WEBPFieldFile
