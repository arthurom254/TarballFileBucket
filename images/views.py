import tarfile
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import io, uuid
import os

TARBALL_PATH = 'media/images.tar'

@csrf_exempt
def upload_image(request):
    if not os.path.exists(TARBALL_PATH):
        with tarfile.open(TARBALL_PATH, 'w') as tar:
            pass

    if request.method == 'POST':
        file = request.FILES.get('image')
        if not file:
            return HttpResponseBadRequest("No file provided")

        extension = os.path.splitext(file.name)[1]  
        unique_filename = f"{uuid.uuid4()}{extension}"

        temp_path = default_storage.save(unique_filename, file)

        with tarfile.open(TARBALL_PATH, 'a') as tar:
            tar.add(temp_path, arcname=unique_filename)

        default_storage.delete(temp_path)

        return JsonResponse({"status": "success", "file_name": unique_filename})
    
    return HttpResponseBadRequest("Only POST method is allowed")

def get_image(request, filename):
    try:
        with tarfile.open(TARBALL_PATH, 'r') as tar:
            try:
                member = tar.getmember(filename)
            except KeyError:
                return HttpResponseBadRequest("File not found in tarball")

            f = tar.extractfile(member)
            if not f:
                return HttpResponseBadRequest("Unable to extract file")

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
        return HttpResponseBadRequest("Tarball not found")

def index(request):
    return render(request, 'index.html')