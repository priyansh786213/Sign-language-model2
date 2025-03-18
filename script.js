let videoElement;
let captureCanvas;
let captureContext;
let outputCanvas;
let outputContext;
let mediaStream = null;
let processingInterval = null;
let recognizedText = "";
let processingActive = false;
let lastProcessedTime = 0;
let frameRateLimit = 5; // Process frames per second
let textHistory = [];
let historyLimit = 5; // Number of letters to keep in history

// DOM elements
document.addEventListener('DOMContentLoaded', () => {
    videoElement = document.getElementById('video-element');
    captureCanvas = document.getElementById('capture-canvas');
    captureContext = captureCanvas.getContext('2d');
    outputCanvas = document.getElementById('output-canvas');
    outputContext = outputCanvas.getContext('2d');
    
    // Set up event listeners
    document.getElementById('start-btn').addEventListener('click', startCapture);
    document.getElementById('stop-btn').addEventListener('click', stopCapture);
    document.getElementById('clear-btn').addEventListener('click', clearText);
    document.getElementById('space-btn').addEventListener('click', addSpace);
    
    // Update UI based on camera availability
    updateCameraUI(false);
});

// Function to start webcam capture
async function startCapture() {
    try {
        // Request webcam access
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            },
            audio: false
        });
        
        // Set video source
        videoElement.srcObject = mediaStream;
        
        // Wait for video to be ready
        videoElement.onloadedmetadata = () => {
            videoElement.play();
            
            // Set canvas dimensions to match video
            captureCanvas.width = videoElement.videoWidth;
            captureCanvas.height = videoElement.videoHeight;
            outputCanvas.width = videoElement.videoWidth;
            outputCanvas.height = videoElement.videoHeight;
            
            // Start processing frames
            processingActive = true;
            processFrame();
            
            // Update UI
            updateCameraUI(true);
            
            // Show success message
            showMessage('Camera started successfully', 'success');
        };
    } catch (error) {
        console.error('Error accessing webcam:', error);
        showMessage('Failed to access camera: ' + error.message, 'danger');
    }
}

// Function to stop webcam capture
function stopCapture() {
    // Stop all tracks in the media stream
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }
    
    // Clear video source
    videoElement.srcObject = null;
    
    // Stop processing
    processingActive = false;
    
    // Update UI
    updateCameraUI(false);
    
    // Show message
    showMessage('Camera stopped', 'info');
}

// Function to process video frames
function processFrame() {
    if (!processingActive) return;
    
    // Limit frame rate for better performance
    const currentTime = Date.now();
    const timeSinceLastProcess = currentTime - lastProcessedTime;
    
    if (timeSinceLastProcess > (1000 / frameRateLimit)) {
        // Update last processed time
        lastProcessedTime = currentTime;
        
        // Draw video frame to canvas
        captureContext.drawImage(videoElement, 0, 0);
        
        // Get image data from canvas
        const imageData = captureCanvas.toDataURL('image/jpeg', 0.8);
        
        // Send to server for processing
        fetch('/process_frame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: imageData })
        })
        .then(response => response.json())
        .then(data => {
            // Update UI with results
            if (data.error) {
                console.error('Error from server:', data.error);
                return;
            }
            
            // Display the processed image
            if (data.processed_image) {
                displayProcessedImage(data.processed_image);
            }
            
            // Update recognized text
            updateRecognizedText(data.text, data.confidence);
        })
        .catch(error => {
            console.error('Error sending frame to server:', error);
        });
    }
    
    // Request the next frame
    requestAnimationFrame(processFrame);
}

// Function to display the processed image
function displayProcessedImage(imageData) {
    const image = new Image();
    image.onload = () => {
        outputContext.clearRect(0, 0, outputCanvas.width, outputCanvas.height);
        outputContext.drawImage(image, 0, 0, outputCanvas.width, outputCanvas.height);
    };
    image.src = imageData;
}

// Function to update the recognized text
function updateRecognizedText(text, confidence) {
    if (!text || text === "No hands detected" || text === "Unknown" || text === "Detecting...") {
        document.getElementById('result-text').textContent = text || "No recognition";
        document.getElementById('confidence-level').style.width = '0%';
        document.getElementById('confidence-text').textContent = '0%';
        return;
    }
    
    // Update the current result display
    document.getElementById('result-text').textContent = text;
    
    // Update confidence display
    const confidencePercent = Math.round(confidence * 100);
    document.getElementById('confidence-level').style.width = confidencePercent + '%';
    document.getElementById('confidence-text').textContent = confidencePercent + '%';
    
    // Update translation if it's a new letter with good confidence
    if (confidence > 0.7) {
        // Check if we're seeing the same letter repeatedly
        if (textHistory.length > 0 && textHistory[textHistory.length - 1] === text) {
            return; // Skip duplicate letters
        }
        
        // Add to history
        textHistory.push(text);
        if (textHistory.length > historyLimit) {
            textHistory.shift();
        }
        
        // Add to the full translation
        const translationElement = document.getElementById('full-translation');
        translationElement.textContent += text;
        
        // Enable the stop button after we get a valid recognition
        document.getElementById('stop-btn').disabled = false;
    }
}

// Function to clear the current text
function clearText() {
    // Clear the translation
    document.getElementById('full-translation').textContent = '';
    textHistory = [];
    
    // Show message
    showMessage('Text cleared', 'info');
}

// Function to add a space to the translation
function addSpace() {
    const translationElement = document.getElementById('full-translation');
    translationElement.textContent += ' ';
    
    // Show message
    showMessage('Space added', 'info');
}

// Function to update the UI based on camera status
function updateCameraUI(cameraActive) {
    document.getElementById('controls-inactive').style.display = cameraActive ? 'none' : 'block';
    document.getElementById('controls-active').style.display = cameraActive ? 'block' : 'none';
    document.getElementById('camera-status').textContent = cameraActive ? 'Camera Active' : 'Camera Inactive';
    document.getElementById('camera-status').className = cameraActive ? 'nav-link active' : 'nav-link';
}

// Function to show a message to the user
function showMessage(message, type) {
    const alertPlaceholder = document.getElementById('alert-placeholder');
    const wrapper = document.createElement('div');
    wrapper.innerHTML = [
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('');
    
    alertPlaceholder.append(wrapper);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        const alert = new bootstrap.Alert(wrapper.querySelector('.alert'));
        alert.close();
    }, 3000);
}
