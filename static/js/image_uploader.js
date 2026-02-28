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
        const svgLeaf = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>`;
        const svgPin = `<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>`;
        const svgTag = `<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.29 9.29a1 1 0 0 0 1.41 0l7.29-7.29a1 1 0 0 0 0-1.41L12 2z"/><circle cx="7" cy="7" r="1.5" fill="currentColor" stroke="none"/></svg>`;

        item.innerHTML = `
            <div class="history-item-top">
                ${entry.imageDataUrl
                    ? `<img class="history-thumb" src="${entry.imageDataUrl}" alt="thumb">`
                    : `<div class="history-thumb-placeholder">${svgLeaf}</div>`
                }
                <div class="history-info">
                    <div class="history-status">${entry.status}</div>
                    <div class="history-confidence">${entry.confidence}</div>
                </div>
            </div>
            <div class="history-meta">
                ${entry.location !== '—' ? `<span class="history-tag">${svgPin} ${entry.location}</span>` : ''}
                ${entry.barcode !== '—' ? `<span class="history-tag">${svgTag} ${entry.barcode}</span>` : ''}
            </div>
            <div class="history-date">${entry.date}</div>
        `;

        // Click to view history record
        item.addEventListener('click', () => {
            // ── Populate result card ──
            statusText.textContent = entry.status;
            statusText.style.color = '#157f3c';
            confidenceText.textContent = entry.confidence;
            treatmentText.textContent = entry.treatment;
            resultBadge.textContent = entry.status;
            resultLocation.textContent = entry.location;
            resultBarcode.textContent = entry.barcode;
            resultCard.style.display = 'block';

            // ── Swap upload box → history image viewer ──
            enterHistoryView(entry.imageDataUrl);

            // ── Highlight active item ──
            document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
        });

        historyList.appendChild(item);
    });
}

// ══════════════════════════════════════════
// ── HISTORY VIEW / UPLOAD BOX SWITCHING ──
// ══════════════════════════════════════════

const dropZoneEl       = document.getElementById('drop-zone');
const historyViewer    = document.getElementById('history-image-viewer');
const historyViewImg   = document.getElementById('history-view-img');
const historyViewNoImg = document.getElementById('history-view-no-img');
const newScanBtn       = document.getElementById('new-scan-btn');

// Switch from upload box → history image viewer
function enterHistoryView(imageUrl) {
    // Hide the entire upload drop zone
    dropZoneEl.style.display = 'none';

    // Show history viewer
    historyViewer.style.display = 'block';

    if (imageUrl) {
        historyViewImg.src = imageUrl;
        historyViewImg.style.display = 'block';
        historyViewNoImg.style.display = 'none';
    } else {
        // No image saved for this record — show placeholder
        historyViewImg.style.display = 'none';
        historyViewNoImg.style.display = 'flex';
    }
}

// Switch back from history viewer → upload box (New Scan)
function exitHistoryView() {
    historyViewer.style.display = 'none';
    dropZoneEl.style.display = 'block';

    // Remove active highlight from all history items
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));

    // Reset result card
    resultCard.style.display = 'none';
}

// "New Scan" button inside the history viewer
newScanBtn.addEventListener('click', exitHistoryView);

// ── Clear history ──
clearHistoryBtn.addEventListener('click', () => {
    if (analysisHistory.length === 0) return;
    if (confirm("Clear all analysis history?")) {
        analysisHistory = [];
        renderHistory();
    }
});

// ══════════════════════════════════════════
// ── LOAD HISTORY FROM DATABASE ──
// ══════════════════════════════════════════
//
// Call this function with a list of records fetched from your Flask/DB route.
//
// Each record in the list should have these fields:
//   {
//     status      : string  — e.g. "Healthy" or "Leaf Blight"
//     confidence  : string  — e.g. "92.4%"
//     treatment   : string  — treatment recommendation text
//     location    : string  — e.g. "Greenhouse A, Row 3"  (use "" or null if none)
//     barcode     : string  — e.g. "PLT-20240601-007"     (use "" or null if none)
//     image_url   : string  — URL or base64 data URL of the scanned image (use "" or null if none)
//     date        : string  — e.g. "2024-06-01 14:32"
//   }
//
// Example usage from Flask (Jinja2 template):
//   <script>
//     const dbRecords = {{ records | tojson }};
//     loadHistoryFromDB(dbRecords);
//   </script>
//
// Example usage with fetch():
//   fetch('/api/history')
//     .then(r => r.json())
//     .then(data => loadHistoryFromDB(data.records));
//
function loadHistoryFromDB(records) {
    if (!Array.isArray(records) || records.length === 0) {
        console.warn('loadHistoryFromDB: no records provided or invalid format.');
        renderHistory();
        return;
    }

    // Normalise each DB record into the internal history entry format
    const normalised = records.map(record => ({
        status      : record.status       || 'Unknown',
        confidence  : record.confidence   || '--%',
        treatment   : record.treatment    || 'No treatment data available.',
        location    : record.location     || '—',
        barcode     : record.barcode      || '—',
        imageDataUrl: record.image_url    || null,
        date        : record.date         || '—'
    }));

    // Replace the in-memory store (newest first — reverse if DB returns oldest first)
    analysisHistory = normalised;

    renderHistory();

    console.log(`loadHistoryFromDB: loaded ${normalised.length} record(s) into history panel.`);
}

// ── Init ──
renderHistory();
