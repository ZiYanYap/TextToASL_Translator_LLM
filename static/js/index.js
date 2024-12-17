document.getElementById('micButton').addEventListener('click', handleMicButtonClick);

function handleMicButtonClick() {
    const button = this;
    const textarea = document.getElementById('input_text');
    const icon = button.querySelector('i');
    
    if (button.classList.contains('recording')) {
        return; // Prevent multiple recordings
    }
    
    button.classList.add('recording');
    icon.classList.replace('fa-microphone', 'fa-microphone-slash');
    
    showToast('Recording...', 'Started recording');
    
    startRecording(button, textarea, icon);
}

async function startRecording(button, textarea, icon) {
    try {
        button.classList.add('processing');
        
        const response = await fetch('/speech-to-text', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            textarea.value = textarea.value
                ? textarea.value + ' ' + data.text
                : data.text;

            submitButton.disabled = !textarea.value.trim();
        } else {
            showToast('Error', data.error || 'Failed to transcribe speech', true);
        }
    } catch (error) {
        showToast('Error', error.message, true);
    } finally {
        button.classList.remove('recording', 'processing');
        icon.classList.replace('fa-microphone-slash', 'fa-microphone');
    }
}

function showToast(title, message, isError = false) {
    const toast = document.getElementById('statusToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    toast.classList.toggle('toast-error', isError);
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

const textarea = document.getElementById('input_text');
const submitButton = document.getElementById('submitButton');

textarea.addEventListener('input', function() {
    submitButton.disabled = !textarea.value.trim();
});

document.addEventListener('DOMContentLoaded', initializeVideoControls);

function initializeVideoControls() {
    const videos = document.querySelectorAll('video');
    const playBtn = document.getElementById('playBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const restartBtn = document.getElementById('restartBtn');
    
    if (videos.length > 0) {
        playBtn.addEventListener('click', () => {
            videos.forEach(video => video.play());
        });

        pauseBtn.addEventListener('click', () => {
            videos.forEach(video => video.pause());
        });

        restartBtn.addEventListener('click', () => {
            videos.forEach(video => {
                video.currentTime = 0;
                video.play();
            });
        });
    }
}

document.getElementById('translationForm').addEventListener('submit', handleTranslationSubmit);

async function handleTranslationSubmit(event) {
    event.preventDefault();
    const textarea = document.getElementById('input_text');
    const outputContainer = document.getElementById('outputContainer');
    const errorContainer = document.getElementById('errorContainer');
    const aslTranslation = document.getElementById('aslTranslation');
    const videoContainer = document.getElementById('videoContainer');
    const videoSource = document.getElementById('videoSource');
    const submitButton = document.getElementById('submitButton');
    const buttonText = document.getElementById('buttonText');
    const buttonSpinner = document.getElementById('buttonSpinner');

    outputContainer.style.display = 'none';
    errorContainer.style.display = 'none';

    // Disable the button and show loading spinner
    submitButton.disabled = true;
    buttonText.style.display = 'none';
    buttonSpinner.style.display = 'inline-block';

    await submitTranslation(textarea, outputContainer, errorContainer, aslTranslation, videoContainer, videoSource, submitButton, buttonText, buttonSpinner);
}

async function submitTranslation(textarea, outputContainer, errorContainer, aslTranslation, videoContainer, videoSource, submitButton, buttonText, buttonSpinner) {
    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input_text: textarea.value })
        });

        const data = await response.json();

        if (response.ok) {
            aslTranslation.textContent = data.asl_translation;
            videoSource.src = data.output_path + '?t=' + new Date().getTime();
            document.getElementById('outputVideo').load();
            videoContainer.style.display = 'flex';
            outputContainer.style.display = 'block';
        } else {
            errorContainer.textContent = data.error;
            errorContainer.style.display = 'block';
        }
    } catch (error) {
        errorContainer.textContent = 'An error occurred: ' + error.message;
        errorContainer.style.display = 'block';
    } finally {
        // Re-enable the button and hide loading spinner
        submitButton.disabled = false;
        buttonText.style.display = 'inline';
        buttonSpinner.style.display = 'none';
    }
}