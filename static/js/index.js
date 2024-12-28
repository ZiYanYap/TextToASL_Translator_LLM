document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const textarea = document.getElementById('input_text');
    const wordCountDisplay = document.getElementById('wordCount');
    const submitButton = document.getElementById('submitButton');
    const errorContainer = document.getElementById('errorContainer');
    const playPauseBtn = document.getElementById('playPauseBtn');

    const MAX_TOKENS = parseInt(wordCountDisplay.getAttribute('data-max-tokens'), 10);

    // Word Count Functionality
    textarea.addEventListener('input', updateWordCount);

    function updateWordCount() {
        const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0); // Filter out empty words
        const tokenCount = words.length;

        // Update the word count display
        wordCountDisplay.textContent = `${tokenCount} / ${MAX_TOKENS} words`;

        // Enable/disable submit button and show errors if over the limit
        if (tokenCount > MAX_TOKENS) {
            showError(`Input too long! Please limit to ${MAX_TOKENS} words.`);
            submitButton.disabled = true;
            wordCountDisplay.classList.add('over-limit'); // Add red styling
            wordCountDisplay.style.color = 'red'; // Change color to red
        } else {
            clearError();
            submitButton.disabled = !textarea.value.trim();
            wordCountDisplay.classList.remove('over-limit');
            wordCountDisplay.style.color = '#fff'; // Revert color to default
        }
    }

    // Show and Clear Errors
    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    }

    function clearError() {
        errorContainer.style.display = 'none';
        errorContainer.textContent = '';
    }

    // Microphone functionality
    document.getElementById('micButton').addEventListener('click', handleMicButtonClick);

    function handleMicButtonClick() {
        const button = this;
        const icon = button.querySelector('i');

        if (button.classList.contains('recording')) return; // Prevent multiple recordings

        button.classList.add('recording');
        icon.classList.replace('fa-microphone', 'fa-microphone-slash');

        showToast('Recording...', 'Started recording');
        startRecording(button, textarea, icon);
    }

    async function startRecording(button, textarea, icon) {
        try {
            button.classList.add('processing');

            const response = await fetch('/api/speech-to-text', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                textarea.value = textarea.value ? `${textarea.value} ${data.text}` : data.text;
                submitButton.disabled = !textarea.value.trim();
                textarea.dispatchEvent(new Event('input')); // Trigger word count update
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

    // Initialize Video Controls
    initializeVideoControls()

    function initializeVideoControls() {
        const video = document.getElementById('outputVideo');
        const restartBtn = document.getElementById('restartBtn');
    
        // Play/Pause button functionality
        playPauseBtn.addEventListener('click', () => {
            if (video.paused) {
                video.play();
                playPauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
            } else {
                video.pause();
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i> Play';
            }
        });
    
        // Restart button functionality
        restartBtn.addEventListener('click', () => {
            video.currentTime = 0;
            video.play();
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
        });
    
        // Reset Play button when the video ends
        video.addEventListener('ended', () => {
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i> Play';
        });
    }

    // Translation submission
    document.getElementById('translationForm').addEventListener('submit', handleTranslationSubmit);

    async function handleTranslationSubmit(event) {
        event.preventDefault();

        const outputContainer = document.getElementById('outputContainer');
        const aslTranslation = document.getElementById('aslTranslation');
        const videoContainer = document.getElementById('videoContainer');
        const videoSource = document.getElementById('videoSource');
        const buttonText = document.getElementById('buttonText');
        const buttonSpinner = document.getElementById('buttonSpinner');

        outputContainer.style.display = 'none';
        videoContainer.style.display = 'none';
        clearError();

        // Reset play/pause button text to "Play"
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i> Play'; // Add this line

        // Disable the button and show loading spinner
        submitButton.disabled = true;
        buttonText.style.display = 'none';
        buttonSpinner.style.display = 'inline-block';

        await submitTranslation(textarea, outputContainer, aslTranslation, videoContainer, videoSource, submitButton, buttonText, buttonSpinner);
    }

    async function submitTranslation(textarea, outputContainer, aslTranslation, videoContainer, videoSource, submitButton, buttonText, buttonSpinner) {
        try {
            const originalText = textarea.value;

            // Step 1: Translate to English
            let response = await fetch('/api/translate-to-english', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input_text: originalText })
            });
            let data = await response.json();
            if (!response.ok) throw new Error(data.error);

            const englishText = data.english_text;

            // Step 2: Convert to ASL
            response = await fetch('/api/convert-to-asl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ english_text: englishText })
            });
            data = await response.json();
            if (!response.ok) throw new Error(data.error);

            const aslText = data.asl_translation;
            aslTranslation.textContent = aslText;
            outputContainer.style.display = 'block';

            // Step 3: Prepare video
            response = await fetch('/api/prepare-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ asl_translation: aslText, context: englishText })
            });
            data = await response.json();
            if (!response.ok) throw new Error(data.error);

            // Step 4: Pose extraction
            response = await fetch('/api/pose-extraction', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            data = await response.json();
            if (!response.ok) throw new Error(data.error);

            videoSource.src = data.output_path + '?t=' + new Date().getTime();
            document.getElementById('outputVideo').load();
            videoContainer.style.display = 'flex';
        } catch (error) {
            showError('An error occurred: ' + error.message);
        } finally {
            submitButton.disabled = false;
            buttonText.style.display = 'inline';
            buttonSpinner.style.display = 'none';
        }
    }
});