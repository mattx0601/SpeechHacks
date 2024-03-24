# SpeechHacks

## Frontend

The frontend is written in Typescript with React Native (expo) along with Reanimated

## Backend

The backend is built using django and handles generating text, analysis of speech, and tone of voice.

The two endpoints that we have set up are described below:

### /upload/str:user_id

This endpoint has an optional param user_id, which branches us into two cases.

If a user_id is provided we assume we are in conversation mode and the return JSON will be formatted as follows:
{
"count": 2, // This number indicates how many corrections were made
"originaltext": original, // Returns the original user's speech but as text
"correctedtext": corrected, // Returns the corrected text
"gptresponse": "", // GPTs response in the conversation
"gptaudio": "" // The audio of GPTs conversation response
"1": ["Many peoples", "Many people"] // Correction 1: [original, corrected]
"2": [...]
}

If a user_id is not provided we assume we are in feedback mode and return JSON as follows:
{
"count": 1, // This number indicates how many corrections were made
"originaltext": original, // Returns the original user's speech but as text
"correctedtext": corrected, // Returns the corrected text
"gptresponse": "", // GPTs feedback
"gptaudio": "" // The audio of GPTs feedback
"1": ["Many peoples", "Many people"] // Correction 1: [original, corrected]
}

### /conv_starter/<str:user_id>/

This endpoint has a required param user_id, this end point is only meant to be used to generate a conversation starter.
The response will be JSON of this format:
{
'message': choice, // The conversation starter in text
'audio': audio // The audio of the conversation starter
}
