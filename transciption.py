import azure.cognitiveservices.speech as speechsdk

def transcribe_audio(subscription_key, region):
    # Set up the speech config
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    # Use the default microphone as the audio source
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # Create a speech recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Open a file to save the transcription
    with open("transcription.txt", "w") as file:
        def recognized_handler(evt):
            # Write final recognized text to the file as a continuous paragraph
            file.write(f"{evt.result.text} ")
            file.flush()  # Ensure text is written to the file immediately
            # Also print the recognized text to the console
            print(evt.result.text, end=" ")

        # Connect the recognized event to the callback function
        speech_recognizer.recognized.connect(recognized_handler)

        # Start continuous speech recognition
        speech_recognizer.start_continuous_recognition()

        try:
            # Keep the application running until the user decides to stop
            input("Press Enter to stop the transcription...\n")
        finally:
            speech_recognizer.stop_continuous_recognition()

# Replace with your Azure subscription key and region
subscription_key = "0bd53904cd384797b19b67b007fa979b" # Replace with your actual key
region = "eastus" # Replace with your actual region
transcribe_audio(subscription_key, region)
