// ── DOM Elements ──
const scanButton = document.getElementById('scan-button');
const statusText = document.getElementById('status-text');
const confidenceText = document.getElementById('confidence-text');
const treatmentText = document.getElementById('treatment-text');
const resultCard = document.getElementById('result-card');
const resultBadge = document.getElementById('result-badge');
const resultLocation = document.getElementById('result-location');
const resultBarcode = document.getElementById('result-barcode');

const locationInput = document.getElementById('location-input');
const barcodeInput = document.getElementById('barcode-input');

const historyList = document.getElementById('history-list');
const historyEmpty = document.getElementById('history-empty');
const historyCount = document.getElementById('history-count');
const clearHistoryBtn = document.getElementById('clear-history-btn');

// ── In-memory history store ──
let analysisHistory = [];

// ── Scan button ──
scanButton.addEventListener('click', async () => {
    if (fileInput.files.length === 0) {
        alert("Please upload an image first!");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('image', file);

    // Update UI: loading state
    statusText.textContent = "Analyzing...";
    statusText.style.color = "orange";
    scanButton.disabled = true;
    document.getElementById('btn-text').textContent = "Processing...";

    // Show result card
    resultCard.style.display = 'block';

    try {
        const response = await fetch('/analayze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        console.log(result);

        if (response.ok) {
            const loc = locationInput.value.trim() || '—';
            const barcode = barcodeInput.value.trim() || '—';

            // Update result card
            statusText.textContent = result.status;
            statusText.style.color = "#157f3c";
            confidenceText.textContent = result.confidence;
            treatmentText.textContent = result.treatment;
            resultBadge.textContent = result.status;
            resultLocation.textContent = loc;
            resultBarcode.textContent = barcode;

            // Save to history
            addToHistory({
                status: result.status,
                confidence: result.confidence,
                treatment: result.treatment,
                location: loc,
                barcode: barcode,
                imageDataUrl: previewImg.src,
                date: new Date().toLocaleString()
            });

        } else {
            statusText.textContent = "Error during analysis";
            statusText.style.color = "red";
            console.error(result.error);
        }

    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = "Connection Failed";
        statusText.style.color = "red";
    } finally {
        scanButton.disabled = false;
        document.getElementById('btn-text').textContent = "Start Analysis";
    }
});

// ── Add to history ──
function addToHistory(entry) {
    analysisHistory.unshift(entry); // newest first
    renderHistory();
}

function renderHistory() {
    historyEmpty.style.display = analysisHistory.length === 0 ? 'flex' : 'none';
    historyCount.textContent = `${analysisHistory.length} scan${analysisHistory.length !== 1 ? 's' : ''}`;

    // Remove old items (keep empty message in DOM)
    const existingItems = historyList.querySelectorAll('.history-item');
    existingItems.forEach(el => el.remove());

    analysisHistory.forEach((entry, index) => {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="history-item-top">
                ${entry.imageDataUrl
                    ? `<img class="history-thumb" src="${entry.imageDataUrl}" alt="thumb">`
                    : `<div class="history-thumb-placeholder">🌿</div>`
                }
                <div class="history-info">
                    <div class="history-status">${entry.status}</div>
                    <div class="history-confidence">${entry.confidence}</div>
                </div>
            </div>
            <div class="history-meta">
                ${entry.location !== '—' ? `<span class="history-tag">📍 ${entry.location}</span>` : ''}
                ${entry.barcode !== '—' ? `<span class="history-tag">🔖 ${entry.barcode}</span>` : ''}
            </div>
            <div class="history-date">${entry.date}</div>
        `;

        // Click to restore result
        item.addEventListener('click', () => {
            statusText.textContent = entry.status;
            statusText.style.color = "#157f3c";
            confidenceText.textContent = entry.confidence;
            treatmentText.textContent = entry.treatment;
            resultBadge.textContent = entry.status;
            resultLocation.textContent = entry.location;
            resultBarcode.textContent = entry.barcode;
            resultCard.style.display = 'block';

            if (entry.imageDataUrl) {
                previewImg.src = entry.imageDataUrl;
                document.getElementById('preview-overlay').style.display = 'block';
                document.getElementById('upload-box-inner').style.display = 'none';
            }
        });

        historyList.appendChild(item);
    });
}

// ── Clear history ──
clearHistoryBtn.addEventListener('click', () => {
    if (analysisHistory.length === 0) return;
    if (confirm("Clear all analysis history?")) {
        analysisHistory = [];
        renderHistory();
    }
});

// Init
renderHistory();
