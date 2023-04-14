#!/usr/local/src/chatgpt-agi/venv/bin/python3

import os
import random
import openai
from gtts import gTTS
from pydub import AudioSegment
from asterisk.agi import AGI

openai.api_key = "<REPLACE ME>"

messages = [
    {"role": "system", "content": "You are a helpful assistant on a phone call."},
]

def send_request(prompt):

    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    
    response = response['choices'][0]['message']['content']
    return response

# Start program
agi = AGI()
callerId = agi.env['agi_callerid']
agi.verbose(f"call from {callerId}")
filepath = "/usr/share/asterisk/sounds"

# Play welcome
agi.stream_file(f"{filepath}/chatgpt-welcome", "1234567890*#")

while True: 
    n = random.randint(1, 9999999999) # generate a random number between 1 and 9999999999
    filename = str(n).zfill(10) # pad with zeros and add extension
    
    agi.verbose("Recording started...")
    agi.record_file(f"{filename}", "wav", "#", 10000, 0, True, 2)
    
    agi.verbose("Recording stopped. Processing now...")
    
    # Cloud Whisper
    audio_file= open(f"{filepath}/{filename}.wav", "rb")
    result = openai.Audio.transcribe("whisper-1", audio_file)

    # Local hosted whisper (to use this, add `import whisper` to the top of this script and commend the two lines for 'cloud whisper')
    #model = whisper.load_model("base")
    #result = model.transcribe(f"{filepath}/{filename}.wav", fp16=False, language='Dutch')
    
    agi.verbose("I heard: " + result["text"])
    prompt = result["text"]
    messages.append({"role": "user", "content": prompt}),
    
    # Send request to OpenAI API
    original_response = send_request(prompt)
    
    # Check if the API call was successful
    if original_response is None:
        agi.verbose("You broke it")
        exit(1)
        
    # Clean up the response
    response = original_response.replace('\n', ' ')
    response = original_response.replace('"', '\'')
    response = original_response.replace('[HANGUP]', '')

    # Return the completed text to Asterisk
    agi.verbose("I got back: " + response)
    agi.set_variable("Result", response)
    messages.append({"role": "assistant", "content": response}),
    
    tts = gTTS(response, lang='nl')
    tts.save(f"{filepath}/{filename}_response.mp3")
    
    # Load the audio file
    sound = AudioSegment.from_file(f"{filepath}/{filename}_response.mp3", format="mp3")
    
    # Set the sample rate to 8kHz
    sound = sound.set_frame_rate(8000)
    
    # Set the number of channels to mono
    sound = sound.set_channels(1)
    
    # Export the audio file as a WAV file
    sound.export(f"{filepath}/{filename}_response.wav", format="wav")
    
    agi.stream_file(f"{filepath}/{filename}_response")
    #agi.appexec('MP3Player', f"{filepath}/{filename}_response.mp3")

    os.remove(f"{filepath}/{filename}.wav") 
    os.remove(f"{filepath}/{filename}_response.mp3") 
    os.remove(f"{filepath}/{filename}_response.wav") 
    
    if original_response.endswith("[HANGUP]"):
      agi.hangup()
