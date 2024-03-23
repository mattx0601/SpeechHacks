from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from transformers import pipeline
from happytransformer import HappyTextToText, TTSettings
from pydub import AudioSegment

speech_to_text_pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
grammar_correction_pipe = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
args = TTSettings(num_beams=5, min_length=1)

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
            retVal = speech_to_text_pipe(file_path)

            return JsonResponse({'message': retVal})
        else:
            return JsonResponse({'error': 'File type not allowed'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def test_audio(request):
    # Hard coded file for now
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "uploads", "grammar.m4a")

    audio = AudioSegment.from_file(file_path, format="m4a")
    wav_audio_file = os.path.join(project_root, "uploads", "converted_audio.wav")
    audio.export(wav_audio_file, format="wav")

    # Perform speech recognition on the uploaded file
    spoken = speech_to_text_pipe(wav_audio_file, generate_kwargs={"language": "english"})
    # Perform grammar correction on the recognized speech
    corrected = grammar_correction_pipe.generate_text(spoken["text"], args=args)


    return JsonResponse({'message': corrected.text})


dict = {
    "count": 0,
    "originaltext": "",
    "correctedtext": "",
    
}

def test_grammar(request):
    # Hard coded file for now
    # Perform grammar correction on the recognized speech
    test = "Many peoples love their country. They're very patriotic."
    testarr = test.split(".")
    corrected = (grammar_correction_pipe.generate_text(test, args=args))
    correctedarr = corrected.text.split(".")
    res_index = [];
    for idx, sentence in enumerate(testarr):
        if (correctedarr[idx] != sentence):
            res_index.append(idx)
        
    dict['count'] = len(res_index)
    dict['originaltext'] = test
    dict['correctedtext'] = corrected.text
    for idx, corr_idx in enumerate(res_index):
        dict[f"{idx + 1}"] = {
            "original": testarr[corr_idx],
            "corrected": correctedarr[corr_idx]
        }
    return JsonResponse(dict)

"""
{
    "count": 1,
    "originaltext": ...,
    "correctedtext": ...,
    "1": { 
        "original": ...,
        "corrected": ...,
     }
     ...

}

"""

# TODO etc
