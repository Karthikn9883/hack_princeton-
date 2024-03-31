const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

// Handle connection success
socket.on('connect', () => {
  console.log('Connected to the transcription server.');
  
  const startButton = document.getElementById('startButton');
  const stopButton = document.getElementById('stopButton');
  
  startButton.disabled = false; // Enable the start button now that we're connected

  startButton.onclick = () => {
    socket.emit('start_transcription', {});
    startButton.disabled = true; // Disable the start button to prevent multiple clicks
    stopButton.disabled = false; // Enable the stop button
  };

  stopButton.onclick = () => {
    socket.emit('stop_transcription', {});
    stopButton.disabled = true; // Disable the stop button after clicking it
    startButton.disabled = false; // Enable the start button again
  };
});

// Handle transcription data received from the server
socket.on('transcribed_text', data => {
  const transcriptionDiv = document.getElementById('transcription');
  transcriptionDiv.textContent += `${data.text}\n`; // Append new text
  transcriptionDiv.scrollTop = transcriptionDiv.scrollHeight; // Auto-scroll
});

// Handle connection errors or disconnections
socket.on('disconnect', () => {
  console.log('Disconnected from the transcription server.');
  document.getElementById('startButton').disabled = true; // Disable the start button when disconnected
});
