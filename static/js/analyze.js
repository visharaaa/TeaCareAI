// ── DOM Elements ──
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewImg = document.getElementById('preview-img');
const previewOverlay = document.getElementById('preview-overlay');
const uploadBoxInner = document.getElementById('upload-box-inner');
const removeImgBtn = document.getElementById('remove-img-btn');

// This file handles the image upload UI interactions for the Analyze page, including:
// - Click to open file dialog
// - Drag & drop support
// - Image preview display
// - Remove image functionality
dropZone.addEventListener('click', (e) => {
    if (e.target === removeImgBtn || removeImgBtn.contains(e.target)) return;
    fileInput.click();
});

// This event is triggered when a user selects a file through the file dialog. 
// It checks if a file is selected and then calls the handleFile function to process and display the image preview.
fileInput.addEventListener('change', function () {
    if (this.files && this.files[0]) handleFile(this.files[0]);
});

// These events handle the drag-and-drop functionality. 
// When a file is dragged over the drop zone, it prevents the default behavior and adds a visual indication. 
// When the file is dropped, it checks if it's an image and processes it accordingly.
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-active');
});


// When the dragged file leaves the drop zone area, this event removes the visual indication by removing the 'drag-active' class.
dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-active');
});

// This event is triggered when a file is dropped onto the drop zone. 
// It prevents the default behavior, removes the visual indication, and checks if the dropped file is an image. If it is, it sets the file input's files to the dropped files and calls the handleFile function to process and display the image preview. 
// If it's not an image, it alerts the user to upload a valid image file.
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-active');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files;
            handleFile(file);
        } else {
            alert("Please upload an image file (JPG, PNG, JPEG).");
        }
    }
});

// This event listener is attached to the "Remove Image" button. 
// When clicked, it prevents the click event from propagating to the drop zone (which would trigger the file dialog) and calls the clearPreview function to reset the image preview and related UI elements.
removeImgBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearPreview();
});

// This function clears the image preview and resets the UI to its initial state.
function clearPreview() {
    previewOverlay.style.display = 'none';
    uploadBoxInner.style.display = 'flex';
    previewImg.src = '';
    fileInput.value = '';
    checkScanReady(); // ← disable scan button when image removed
}

// This function takes a file as input, reads it using a FileReader, and sets the preview image source to the file's data URL. 
// It also updates the UI to show the preview and hide the upload box. Finally, it calls checkScanReady to enable the scan button if all conditions are met.
function handleFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        previewImg.src = e.target.result;
        previewOverlay.style.display = 'block';
        uploadBoxInner.style.display = 'none';
        checkScanReady(); // ← enable scan button if all conditions met
    };
    reader.readAsDataURL(file);
}