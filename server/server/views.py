from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from transformers import pipeline

pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'aac'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@csrf_exempt
def index(request):
    return JsonResponse({'message': 'Hello, world!'})

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file part'}, status=400)
        
        if file.name == '':
            return JsonResponse({'error': 'No selected file'}, status=400)

        if allowed_file(file.name):
            filename = file.name
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Perform speech recognition on the uploaded file
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            retVal = pipe(file_path)

            return JsonResponse({'message': retVal})
        else:
            return JsonResponse({'error': 'File type not allowed'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def test_audio(request):
    filename = "testing.flac"
    ret = pipe("") # file_path = os.path.join(settings.MEDIA_ROOT, filename))
    return JsonResponse({'message': ret})

# TODO get the file to pass into pipeline and return the result correctly, connect front end to back end(just make sure the post request is working correctly)
# TODO etc
