import os
import sys
from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management.base import BaseCommand
from PIL import Image
from posts.models import Post


class Command(BaseCommand):
    help = "Convert all images to WebP format"

    def handle(self, *args, **options):
        for obj in Post.objects.all():
            # if obj.image and not obj.image.name.lower().endswith(".webp"):
            if obj.image:
                self.stdout.write(f"'{obj.image.name}' в процессе.")
                img_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
                img = Image.open(img_path)
                img = img.convert("RGB")
                output = BytesIO()
                img.save(output, format="WEBP")
                output.seek(0)
                new_name = f"{obj.image.name.split('.')[0].split('/')[-1]}.webp"
                new_image = InMemoryUploadedFile(
                    output,
                    "ImageField",
                    new_name,
                    "image/webp",
                    sys.getsizeof(output),
                    None,
                )
                obj.image.save(new_name, new_image, save=False)
                obj.save()
                os.remove(img_path)
                self.stdout.write(f"{obj.image.name} конвертировано в формат WebP")
        self.stdout.write(
            self.style.SUCCESS("Все изображения конвертированы в формат WebP")
        )
