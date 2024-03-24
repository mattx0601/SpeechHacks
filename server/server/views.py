from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from transformers import pipeline
from happytransformer import HappyTextToText, TTSettings
from pydub import AudioSegment
from openai import OpenAI 
from pathlib import Path
from dotenv import load_dotenv 
load_dotenv()

client = OpenAI()

user_dict = {
    "0" : [],
    "1" : [],
}
speech_to_text_pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
grammar_correction_pipe = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
text_to_speech_pipe = pipeline("text2text-generation", model ="lmsys/fastchat-t5-3b-v1.0")

args = TTSettings(num_beams=5, min_length=1)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'aac'}

def file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

@csrf_exempt
def index(request):
    return JsonResponse({'message': 'Hello, world!'})

@csrf_exempt
def upload_file(request,  user_id=None ):
    # For POST methods only
    if request.method == 'POST':
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file = request.FILES.get('file')

        file_ext = file_extension(file.name)
        if not file:
            return JsonResponse({'error': 'No file part'}, status=400)
        if file.name == '':
            return JsonResponse({'error': 'No selected file'}, status=400)
        
        file_path = os.path.join(project_root, "uploads", file.name)
        try:
            audio = AudioSegment.from_file(file_path, format=file_ext)
            wav_audio_file = os.path.join(project_root, "uploads", "converted_audio.wav")
            audio.export(wav_audio_file, format="wav")

            #  Perform speech recognition on the uploaded file
            #  Perform speech recognition on the uploaded file
            spoken = speech_to_text_pipe(wav_audio_file, generate_kwargs={"language": "english"})
            
            # Perform grammar correction on the recognized speech
            # Perform grammar correction on the recognized speech
            corrected = grammar_correction_pipe.generate_text(spoken["text"], args=args)

            return correction(spoken["text"], corrected.text, user_id) # JsonResponse({'message': corrected.text})
        except:
            return JsonResponse({'error': 'File type not allowed'}, status=400)

            
        else:
            return JsonResponse({'error': 'File type not allowed'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def correction(original, corrected, user_id):
    original_arr = original.split(".")
    corrected_arr = corrected.split(".")
    corrections_dict = {
        "count": 0,
        "originaltext": original,
        "correctedtext": corrected,
        "gptresponse": "",
        "gptaudio": ""
    }

    res_index = []
    for idx, sentence in enumerate(original_arr):
        if (corrected_arr[idx] != sentence):
            res_index.append(idx)

    corrections_dict['count'] = len(res_index)

    for idx, corr_idx in enumerate(res_index):
        corrections_dict[f"{idx + 1}"] = {
            "original": original_arr[corr_idx],
            "corrected": corrected_arr[corr_idx]
        }

    if (user_id):
        # save to database
        corrections_dict["gptresponse"] = gpt_conversation(original, user_id)
        corrections_dict["gptaudio"] = gpt_audio(corrections_dict["gptresponse"])
    else:
        corrections_dict["gptresponse"] = gpt_corrections(original)
        corrections_dict["gptaudio"] = gpt_audio(corrections_dict["gptresponse"])
    
    return JsonResponse(corrections_dict)




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

def gpt_conversation(user_input, user_id):
    """Handles a single turn of conversation with ChatGPT, maintaining context."""
    user_dict[user_id].append(user_input)

    prompt =  "Respond to the conversation as a normal everyday passing human named Server and keep the conversation going \n"
    if len(user_dict[user_id]) <= 3:
        index = 0
        for message in user_dict[user_id]:
            if index % 2 == 0:
                prompt += f"Server: {message}\n"
            else:
                prompt += f"User: {message}\n"
            index +=1
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust the model as needed
            messages=[{"role": "system", "content": prompt}]
        )
        if "Server:" in response.choices[0].message.content:
            chatgpt_response = (response.choices[0].message.content)[8:]
        elif "User:" in response.choices[0].message.content:
            chatgpt_response = (response.choices[0].message.content)[6:]
        else: 
            chatgpt_response = (response.choices[0].message.content)
        user_dict[user_id].append(chatgpt_response)

        return chatgpt_response
    else:
        index = len(user_dict[user_id]) - 4
        for message in user_dict[user_id][-3:]:
            if index % 2 == 0:
                prompt += f"Server: {message}\n"
            else:
                prompt += f"User: {message}\n"
            index +=1
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust the model as needed
            messages=[{"role": "system", "content": prompt}]
        )
        if "Server:" in response.choices[0].message.content:
            chatgpt_response = (response.choices[0].message.content)[8:]
        elif "User:" in response.choices[0].message.content:
            chatgpt_response = (response.choices[0].message.content)[6:]
        else:
            chatgpt_response = (response.choices[0].message.content) # Server: I am well.
        user_dict[user_id].append(chatgpt_response)

        return chatgpt_response
    
def text_to_audio(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    response.with_streaming_response.method(speech_file_path)
    return speech_file_path