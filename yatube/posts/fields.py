import io
import os
import sys

from django.core.files.base import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image


class WEBPFieldFile(ImageFieldFile):
    """
    Класс наследник от ImageFieldFile, который производит
    сохранение файла с автоматической конвертацией в WEBP формат.
    """

    def save(self, name: str, content: File, save: bool = True) -> None:
        content.file.seek(0)
        image = Image.open(content.file)
        image = image.convert("RGB")
        image_bytes = io.BytesIO()
        image.save(fp=image_bytes, format="WEBP")
        image_bytes.seek(0)
        name = f"{os.path.splitext(name)[0]}.webp"
        # image_content_file = ContentFile(content=image_bytes.getvalue())
        image_content_file = InMemoryUploadedFile(
            image_bytes,
            "ImageField",
            name,
            "image/webp",
            sys.getsizeof(image_bytes),
            None,
        )
        super().save(name, image_content_file, save)


class WEBPField(models.ImageField):
    """
    Класс наследник от ImageField,
    который использует WEBPFieldFile вместо ImageFieldFile.
    """

    attr_class = WEBPFieldFile
