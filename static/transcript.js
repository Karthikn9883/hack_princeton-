// Please replace 'YourAzureSubscriptionKey' and 'YourAzureServiceRegion' with your actual key and region.
const speechConfig = SpeechSDK.SpeechConfig.fromSubscription('5c82e47eb69546caacab253c9236b122', 'eastus');
speechConfig.speechRecognitionLanguage = 'en-US';

const startTranscriptionButton = document.getElementById('startTranscription');
const stopTranscriptionButton = document.getElementById('stopTranscription');
const transcriptionResults = document.getElementById('transcriptionResults');

let recognizer;
let isTranscribing = false;
let transcription = '';

startTranscriptionButton.addEventListener('click', () => {
    isTranscribing = true;
    stopTranscriptionButton.disabled = false;
    startTranscriptionButton.disabled = true;
    transcriptionResults.textContent = ''; // Clear previous results

    const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
    recognizer = new SpeechSDK.SpeechRecognizer(speechConfig, audioConfig);

    recognizer.recognizing = (sender, event) => {
        transcriptionResults.textContent += event.result.text + ' ';
    };

    recognizer.recognized = (sender, event) => {
        transcription += event.result.text + '\n';
    };

    recognizer.startContinuousRecognitionAsync();
});

stopTranscriptionButton.addEventListener('click', () => {
    if (!isTranscribing) return;

    recognizer.stopContinuousRecognitionAsync(() => {
        recognizer.close();
        recognizer = undefined;
        isTranscribing = false;
        stopTranscriptionButton.disabled = true;
        startTranscriptionButton.disabled = false;

        // Send the transcription to the server to save it
        fetch('/save_transcript', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript: transcription })
        })
        .then(response => response.json())
        .then(data => console.log(data.message))
        .catch(error => console.error('Error:', error));

        transcription = ''; // Reset transcription
    }, (err) => {
        console.error('Error stopping recognition:', err);
    });
});