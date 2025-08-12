import streamlit as st
import asyncio
import io
from gtts import gTTS
import openai
import speech_recognition as sr


# Streamlit app configuration
st.set_page_config(page_title="Conversational Voice Bot", layout="wide")


st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        color: #4CAF50;  /* Change the color to your preference */
        font-size: 40px;  /* Adjust the font size as needed */
        margin-top: 20px; /* Adds space from the top of the page */
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)


st.markdown('<div class="centered-title">Jawad Ahmad Conversational Voice Bot</div>', unsafe_allow_html=True)
# OpenAI API key
openai.api_key = "yahan_apna_key_dalo"
# UI colors for messages
USER_COLOR = "#DFF6FF"  
GPT_COLOR = "#FFEDD6"  

# Function to listen to user input
async def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        # Transcribe audio
        transcription = recognizer.recognize_google(audio)
        return transcription, audio.get_wav_data()
    
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand you.", None

# Function to get GPT response
def get_gpt_response(conversation_history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    return response['choices'][0]['message']['content']

# Function to generate and return speech as an audio file
async def speak_and_play(text):
    tts = gTTS(text, lang="en")
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Reset the pointer to the start of the file
    return audio_file

def display_conversation():
    entry2 = st.session_state["conversation"][-1]
    entry1 = st.session_state["conversation"][-2]


    print(type(entry1["audio"]))
    if entry1["role"] == "user":
        col1, col2 = st.columns([2, 1])
        with col2:
            # Display user audio with a unique key
            if entry1["audio"]:
                st.audio(entry1["audio"], format="audio/wav", autoplay=False)
            st.markdown(
                f"<div style='background-color: {USER_COLOR}; padding: 10px; border-radius: 10px; text-align: right;'>{entry1['text']}</div>",
                unsafe_allow_html=True,
            )
            
        with col1:
            st.empty()
    if entry2["role"] == "assistant":

        col1, col2 = st.columns([1, 2])
        with col1:
            # Display assistant audio with a unique key
            if entry2["audio"]:
                st.audio(entry2["audio"], format="audio/mp3", autoplay=True)
            
            # audio_html = generate_audio_html(entry2["audio"])

            st.markdown(
                f"<div style='background-color: {GPT_COLOR}; padding: 10px; border-radius: 10px; text-align: left;'>{entry2['text']}</div>",
                unsafe_allow_html=True,

            )

            
        with col2:
            st.empty()

# Main conversation loop
async def conversation_loop():
    while True:
        # Listen to user only once per cycle
        transcription, user_audio = await listen_to_user()
        if not transcription or transcription.lower() in ["quit", "exit"]:
            st.write("Ending conversation...")
            break

        # Avoid repeating recent messages
        if len(st.session_state["conversation"]) > 0 and st.session_state["conversation"][-1]["text"] == transcription:
            continue  # Skip adding this message to history

        # Add user's input to the conversation history
        st.session_state["conversation"].append({
            "role": "user",
            "text": transcription,
            "audio": user_audio  # Store audio data separately
        })


        # Get GPT response using full conversation history (text only)
        response = get_gpt_response([
            {"role": entry["role"], "content": entry["text"]}
            for entry in st.session_state["conversation"]
        ])

        # Generate response audio
        response_audio = await speak_and_play(response)

        # Add GPT's response to the conversation history
        st.session_state["conversation"].append({
            "role": "assistant",
            "text": response,
            "audio": response_audio  # Store audio data separately
        })

        print(len(st.session_state["conversation"]))

        # Update the displayed conversation
        display_conversation()

#  driver function
async def main():
    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []
    
    st.write("Starting conversation...")
    await conversation_loop()


if __name__ == "__main__":
    asyncio.run(main())