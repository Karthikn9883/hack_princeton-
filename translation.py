import azure.cognitiveservices.speech as speechsdk

def translate_speech(subscription_key, region, from_language, to_languages):
    # Set up the speech translation configuration
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=subscription_key, region=region,
        speech_recognition_language=from_language,
        target_languages=to_languages)
    
    # Use the default microphone as the audio source
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # Create a translation recognizer
    translator = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config)

    def translating_handler(evt):
        # Extract translations from the event
        translations = evt.result.translations
        # Print the translations to the console
        for lang, text in translations.items():
            print(f"Translation to {lang}: {text}")

    # Connect the translating event to the callback function
    translator.recognized.connect(translating_handler)

    # Start continuous speech recognition and translation
    translator.start_continuous_recognition()

    try:
        # Keep the application running until the user decides to stop
        input("Press Enter to stop the translation...\n")
    finally:
        translator.stop_continuous_recognition()

# Replace with your Azure subscription key and region
subscription_key = "0bd53904cd384797b19b67b007fa979b" # Replace with your actual key
region = "eastus" # Replace with your actual region
from_language = "en-US" # The language spoken in the meeting
to_languages = ["en", "hi"] # The languages to translate the meeting into

translate_speech(subscription_key, region, from_language, to_languages)
