// Select the necessary DOM elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewImg = document.getElementById('preview-img');
const imagePreviewBox = document.getElementById('image-preview-box');
const noImageText = imagePreviewBox.querySelector('p'); // Gets the "No Image Selected" text

// 1. Click to upload functionality
dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
    handleFile(this.files[0]);
    }
});

// 2. Drag and Drop functionality
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault(); // Prevents the browser from opening the image in a new tab
    dropZone.classList.add('drag-active');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-active');
});


dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-active');

    // Check if files were dropped
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];

        // Validate that the file is an image
        if (file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files; // Sync the dropped file to the hidden input
                handleFile(file);
        } else {
            alert("Please upload an image file (JPG, PNG, JPEG).");
        }
    }
});


// 3. Function to read the file and update the preview
function handleFile(file) {
    const reader = new FileReader();

        reader.onload = function(e) {
        // Update the image source and display it
        previewImg.src = e.target.result;
        previewImg.style.display = 'block';

        // Hide the "No Image Selected" text
        if (noImageText) {
            noImageText.style.display = 'none';
        }
    }

    // Read the image file as a data URL
    reader.readAsDataURL(file);
}
