// ── DOM Elements ──
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewImg = document.getElementById('preview-img');
const previewOverlay = document.getElementById('preview-overlay');
const uploadBoxInner = document.getElementById('upload-box-inner');
const removeImgBtn = document.getElementById('remove-img-btn');

// ── Click to browse ──
dropZone.addEventListener('click', (e) => {
    if (e.target === removeImgBtn || removeImgBtn.contains(e.target)) return;
    fileInput.click();
});

fileInput.addEventListener('change', function () {
    if (this.files && this.files[0]) handleFile(this.files[0]);
});

// ── Drag & Drop ──
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-active');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-active');
});

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

// ── Remove image button ──
removeImgBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearPreview();
});

function clearPreview() {
    previewOverlay.style.display = 'none';
    uploadBoxInner.style.display = 'flex';
    previewImg.src = '';
    fileInput.value = '';
}

// ── Handle file & show preview ──
function handleFile(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        previewImg.src = e.target.result;
        previewOverlay.style.display = 'block';
        uploadBoxInner.style.display = 'none';
    };
    reader.readAsDataURL(file);
}
