import os
import tarfile
import uuid
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ImageUploadSerializer
from .models import UploadedFile
from django.http import HttpResponse

TARBALL_PATH = 'media/files.tar'

class ImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error": "No file provided or invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['image']
        extension = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4()}{extension}"

        if not os.path.exists(TARBALL_PATH):
            with tarfile.open(TARBALL_PATH, 'w') as tar:
                pass

        temp_path = default_storage.save(unique_filename, file)

        with tarfile.open(TARBALL_PATH, 'a') as tar:
            tar.add(temp_path, arcname=unique_filename)

        default_storage.delete(temp_path)
        upload=UploadedFile.objects.create(file_name=unique_filename)
        url=request.build_absolute_uri(reverse('get_file', args=(upload.file_name, )))
        return Response({"status": "success", "file_name": upload.file_name, "url":url}, status=status.HTTP_201_CREATED)


class GetImageView(APIView):
    def get(self, request, filename, *args, **kwargs):
        try:
            with tarfile.open(TARBALL_PATH, 'r') as tar:
                try:
                    member = tar.getmember(filename)
                except KeyError:
                    return Response({"error": "File not found in the bucket"}, status=status.HTTP_400_BAD_REQUEST)

                f = tar.extractfile(member)
                if not f:
                    return Response({"error": "Unable to extract file"}, status=status.HTTP_400_BAD_REQUEST)

                range_header = request.headers.get('Range', None)
                if not range_header:
                    return HttpResponse(f.read(), content_type='image/jpeg')

                size = member.size
                byte_range = range_header.split('=')[1]
                byte_start, byte_end = 0, size - 1

                if '-' in byte_range:
                    byte_start, byte_end = [int(x) if x else None for x in byte_range.split('-')]
                byte_end = byte_end if byte_end is not None else size - 1

                f.seek(byte_start)
                data = f.read(byte_end - byte_start + 1)

                response = HttpResponse(data, status=206, content_type='image/jpeg')
                response['Content-Range'] = f'bytes {byte_start}-{byte_end}/{size}'
                response['Accept-Ranges'] = 'bytes'
                return response

        except FileNotFoundError:
            return Response({"error": "Tarball not found"}, status=status.HTTP_400_BAD_REQUEST)

def index(request):
    return render(request, 'index.html')