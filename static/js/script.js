const video = document.getElementById('webcam');

// Reference the new predicted label box element
const predictedLabelBox = document.getElementById('predicted-label-box');
const predictedLabelElement = document.getElementById('predicted-label');

navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        video.srcObject = stream;
    })
    .catch((error) => {
        console.error('Error accessing webcam:', error);
    });

// Function to mirror the video horizontally
function mirrorVideo() {
    video.style.transform = 'scaleX(-1)';
}

// Call the mirrorVideo function to mirror the video
mirrorVideo();

// Function to send a frame to the server for processing
function sendFrameToServer() {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');

    // Use AJAX to send the frame data to the server
    fetch('/video_feed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ frame: imageData.split(',')[1] }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text(); // Use text() instead of json()
    })
    .then(data => {
        if (data.trim() === '') {
            throw new Error('Empty response from the server.');
        }
        return JSON.parse(data);
    })
    .then(data => {
        console.log('Predicted Labels:', data.predicted_labels);
        predictedLabelElement.textContent = data.predicted_labels;
    })
    
    .catch(error => {
        console.error('Error sending frame to server:', error);
    });
}

// Periodically send frames to the server (adjust the interval as needed)
setInterval(sendFrameToServer, 1000);
