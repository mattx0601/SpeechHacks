import random
from django.http import JsonResponse, FileResponse
import base64
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from transformers import pipeline   
from happytransformer import HappyTextToText, TTSettings
from pydub import AudioSegment
from openai import OpenAI 
from pathlib import Path
from dotenv import load_dotenv 
import json 

with open("../server/server/database.json", 'r') as file:
    user_dict = json.load(file)

load_dotenv()

client = OpenAI()

speech_to_text_pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
grammar_correction_pipe = HappyTextToText("T5", "vennify/t5-base-grammar-correction")

args = TTSettings(num_beams=5, min_length=1)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'aac'}

def file_extension(filename):
    """Returns the file extension of the given filename."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

@csrf_exempt
def index(request):
    """Returns a simple JSON response with a message."""
    return JsonResponse({'message': 'Hello, world!'})

@csrf_exempt
def upload_file(request,  user_id=None ):
    """Handles file uploads and performs speech recognition and grammar correction."""

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
            spoken = speech_to_text_pipe(wav_audio_file, generate_kwargs={"language": "english"})
            
            # Perform grammar correction on the recognized speech
            # Perform grammar correction on the recognized speech
            corrected = grammar_correction_pipe.generate_text(spoken["text"], args=args)

            return correction(spoken["text"], corrected.text, user_id) # JsonResponse({'message': corrected.text})
        except:
            return JsonResponse({'error': 'File type not allowed'}, status=400)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def correction(original, corrected, user_id):
    """Returns a JSON response with the original and corrected text, the number of corrections, and the GPT response and audio."""

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
        confidence = confidence_correction(original)
        corrections_dict["gptresponse"] = gpt_corrections(corrections_dict["count"], confidence)
        corrections_dict["gptaudio"] = gpt_audio(corrections_dict["gptresponse"])

    return JsonResponse(corrections_dict)

def confidence_correction(text):
    """Returns a boolean depending on the confidence derived from the speech, this is determined by the number of ums and ahs in the speech."""
    confidence = True
    ums = text.count("um")
    ahs = text.count("ah")
    dots = text.count("..")
    if ums + ahs + dots > 1:
        confidence = False
    return confidence

def gpt_corrections(count, confidence): #TODO update text to be more helpful
    """Returns a string based on the number of grammatical errors in the text."""

    if count == 0 and confidence == True:
        retString = "Your speech had no grammatical errors and you spoke confidently! Great job!"
    elif count == 0 and confidence == False:
        retString = "You spoke grammatically correct, but there were many filler words. Try to speak more clearly."
    elif confidence == True:
        retString = f"Your tone and confidence were good, but I found {count} errors in the text. Lets take a look at the corrections."
    else:
        retString = f"You've used numerous filler words. Aim for a more confident tone in your speech. I've identified {count} errors within the text. Let's examine the corrections together."
    return retString

"Try to focus on ennunciating your words clearly and speaking with more confidence."

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
        user_dict = save_data(user_dict)
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
        save_data(user_dict)
        return chatgpt_response

def gpt_audio(text, user_id):
    """Generates an audio file from the given text."""

    speech_file_path = Path(__file__).parent.parent / f"uploads/speech{user_id}-{len(user_dict[user_id])}.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return str(speech_file_path)

CONV_STARTERS = ["Hey, how are you doing!", "What's up?", "How's your day going?"]

def conversation_starter(request):
    """Returns a conversation starter and adds it to the user's conversation history."""

    user_id = request.GET.get('user_id')

    print(user_id)
    if user_id is None:
        return JsonResponse({'error': 'User ID not provided'}, status=400)
    choice = random.choice(CONV_STARTERS)
    user_dict[user_id] = [choice]
    file_path_to_audio = gpt_audio(choice, user_id)
    return JsonResponse({'message': choice, 'audio': file_path_to_audio})

def return_audio(request):
    file_path_to_audio = request.GET.get('file_path_to_audio')
    return FileResponse(open(file_path_to_audio, 'rb'))

""" Test functions below"""


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
def test_conversation(request, id):
    print(id)
    conversation_starter(id)
    return JsonResponse({'message': 'Conversation started'})

def save_data(data):
    try:
        with open('database.json', 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}
    merged_data = {**existing_data, **data}
    with open("../server/server/database.json", 'w') as file:
        json.dump(merged_data, file, indent=4)
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
