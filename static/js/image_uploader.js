// ── DOM Elements ──
const scanButton       = document.getElementById('scan-button');
const statusText       = document.getElementById('status-text');
const confidenceText   = document.getElementById('confidence-text');
const treatmentText    = document.getElementById('treatment-text');
const resultCard       = document.getElementById('result-card');
const resultBadge      = document.getElementById('result-badge');
const resultBarcode    = document.getElementById('result-barcode');
const resultField      = document.getElementById('result-field');

const barcodeInput     = document.getElementById('barcode-input');
const locationLatInput = document.getElementById('location-lat');
const locationLngInput = document.getElementById('location-lng');
const fieldSelect      = document.getElementById('field-select');

const historyList      = document.getElementById('history-list');
const historyEmpty     = document.getElementById('history-empty');
const historyCount     = document.getElementById('history-count');
const clearHistoryBtn  = document.getElementById('clear-history-btn');

// ── In-memory history store ──
let analysisHistory = [];


// ══════════════════════════════════════════
// ── BUTTON ENABLE / DISABLE GUARD ──
// ══════════════════════════════════════════

function checkScanReady() {
    const hasImage   = fileInput.files.length > 0;
    const hasField   = fieldSelect.value !== '';
    const hasBarcode = barcodeInput.value.trim() !== '';

    const ready = hasImage && hasField && hasBarcode;
    scanButton.disabled      = !ready;
    scanButton.style.opacity = ready ? '1' : '0.45';
    scanButton.style.cursor  = ready ? 'pointer' : 'not-allowed';
}

// Disable on page load
scanButton.disabled      = true;
scanButton.style.opacity = '0.45';
scanButton.style.cursor  = 'not-allowed';

// Watch field and barcode directly
// Image state is handled by analyze.js which calls checkScanReady() directly
fieldSelect.addEventListener('change', checkScanReady);
barcodeInput.addEventListener('input', checkScanReady);


// ══════════════════════════════════════════
// ── FIELD DROPDOWN — fetch from Flask ──
// ══════════════════════════════════════════

(async function loadFields() {
    const spinner  = document.getElementById('field-select-loading');
    const arrow    = document.getElementById('field-select-arrow');
    const errorMsg = document.getElementById('field-select-error');

    if (!spinner || !arrow || !errorMsg) return;

    spinner.style.display = 'block';

    try {
        const res  = await fetch('/api/fields');
        if (!res.ok) throw new Error('Request failed');
        const fields = await res.json();

        fieldSelect.innerHTML = '';

        if (fields.length === 0) {
            fieldSelect.innerHTML = '<option value="">No fields found</option>';
            const warn = document.getElementById('no-fields-warning');
            if (warn) warn.style.display = 'flex';
        } else {
            fieldSelect.innerHTML = '<option value="">— Select a field —</option>';
            fields.forEach(f => {
                const opt = document.createElement('option');
                opt.value       = f.field_id;
                opt.textContent = f.field_name;
                fieldSelect.appendChild(opt);
            });
            fieldSelect.disabled = false;
        }

        spinner.style.display = 'none';
        arrow.style.display   = 'block';
        checkScanReady();

    } catch (err) {
        console.error('Failed to load fields:', err);
        fieldSelect.innerHTML  = '<option value="">Could not load fields</option>';
        spinner.style.display  = 'none';
        arrow.style.display    = 'block';
        errorMsg.style.display = 'block';
    }
})();


// ══════════════════════════════════════════
// ── BARCODE DROPDOWN — toggle custom list
// ══════════════════════════════════════════

let barcodeCodes    = [];
let barcodesLoaded  = false;

async function fetchBarcodeCodes() {
    if (barcodesLoaded) return;
    const loadingEl = document.getElementById('barcode-dropdown-loading');
    try {
        const res   = await fetch('/api/chat-codes');
        if (!res.ok) throw new Error('Request failed');
        barcodeCodes   = await res.json();
        barcodesLoaded = true;
        renderBarcodeList(barcodeCodes);
    } catch (err) {
        console.error('Failed to load barcodes:', err);
        if (loadingEl) loadingEl.textContent = 'Could not load barcodes.';
    }
}

function renderBarcodeList(codes) {
    const list = document.getElementById('barcode-dropdown-list');
    if (!list) return;
    list.innerHTML = '';

    if (!codes || codes.length === 0) {
        list.innerHTML = '<div class="barcode-dropdown-loading">No existing barcodes.</div>';
        return;
    }

    codes.forEach(c => {
        const item       = document.createElement('div');
        item.className   = 'barcode-dropdown-item';
        item.textContent = c.chat_code;
        item.addEventListener('click', () => {
            barcodeInput.value = c.chat_code;
            closeBarcodeDropdown();
            checkScanReady();
        });
        list.appendChild(item);
    });
}

function toggleBarcodeDropdown() {
    const list = document.getElementById('barcode-dropdown-list');
    const btn  = document.getElementById('barcode-dropdown-btn');
    if (!list) return;

    const isOpen = list.style.display !== 'none';
    if (isOpen) {
        closeBarcodeDropdown();
    } else {
        list.style.display = 'block';
        btn.classList.add('open');
        fetchBarcodeCodes();
        // close when clicking outside
        setTimeout(() => document.addEventListener('click', outsideClickHandler), 0);
    }
}

function closeBarcodeDropdown() {
    const list = document.getElementById('barcode-dropdown-list');
    const btn  = document.getElementById('barcode-dropdown-btn');
    if (list) list.style.display = 'none';
    if (btn)  btn.classList.remove('open');
    document.removeEventListener('click', outsideClickHandler);
}

function outsideClickHandler(e) {
    const wrap = document.querySelector('.barcode-combo-wrap');
    if (wrap && !wrap.contains(e.target)) {
        closeBarcodeDropdown();
    }
}



// ══════════════════════════════════════════
// ── RAG TREATMENT FORMATTER ──
// ══════════════════════════════════════════

function formatRAGOutput(ragInput) {
    let rawText, confidence, refId;
    if (Array.isArray(ragInput)) {
        [rawText, confidence, refId] = ragInput;
    } else {
        rawText = ragInput;
        confidence = null;
        refId = null;
    }
    return {
        sections:   _parseIntoSections(String(rawText || '')),
        confidence: confidence !== null ? _parseConfidence(confidence) : null,
        refId:      refId || null,
        rawText,
    };
}

function renderRAGToHTML(formatted) {
    const { sections, confidence, refId } = formatted;
    const sectionIcons = {
        'Symptoms': '🍃',
        'Treatments': '💊',
        'Practical Tips for Local Farmers': '🌱',
        'Safety Note': '⚠️',
    };

    const sectionsHTML = sections.map(section => {
        const headingHTML = section.heading
            ? `<h4 class="rag-heading">${sectionIcons[section.heading] ?? '📌'} ${_escHTML(section.heading)}</h4>`
            : '';
        const isList    = section.items.some(i => i.type === 'bullet' || i.type === 'numbered');
        const isOrdered = isList && section.items.every(i => i.type === 'numbered');
        const tag       = isList ? (isOrdered ? 'ol' : 'ul') : 'div';
        const itemsHTML = section.items.map(item => {
            const inner = item.parts
                .map(p => p.bold ? `<strong>${_escHTML(p.text)}</strong>` : _escHTML(p.text))
                .join('');
            return isList ? `<li>${inner}</li>` : `<p class="rag-para">${inner}</p>`;
        }).join('\n');
        return `<div class="rag-section">${headingHTML}<${tag} class="rag-list">${itemsHTML}</${tag}></div>`;
    }).join('\n');

    let footerHTML = '';
    if (confidence || refId) {
        const badge = confidence
            ? `<span class="rag-confidence-badge" style="color:${confidence.color};border-color:${confidence.color}">
                 ● ${_capitalize(confidence.level)} — ${confidence.value}%
               </span>`
            : '';
        const ref = refId ? `<span class="rag-ref">REF: ${_escHTML(refId)}</span>` : '';
        footerHTML = `<div class="rag-footer">${badge}${ref}</div>`;
    }
    return `<div class="rag-output">${sectionsHTML}${footerHTML}</div>`;
}

function _parseIntoSections(text) {
    const lines = text.split('\n').map(l => l.trim());
    const sections = [];
    let currentSection = null;
    let introParagraphs = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (!line) continue;
        const headingMatch = line.match(/^\*\*(.+?)\**:?\*\*:?$/);
        if (headingMatch) {
            if (introParagraphs.length && !sections.length) {
                sections.push({ type: 'intro', heading: null, items: introParagraphs });
                introParagraphs = [];
            }
            if (currentSection) sections.push(currentSection);
            currentSection = { type: 'section', heading: headingMatch[1].replace(/:$/, '').trim(), items: [] };
        } else if (line.startsWith('• ') || line.startsWith('- ')) {
            const content = line.replace(/^[•\-]\s+/, '');
            if (currentSection) currentSection.items.push({ type: 'bullet', ..._parseInline(content) });
        } else if (/^\d+\.\s/.test(line)) {
            const content = line.replace(/^\d+\.\s/, '');
            if (currentSection) currentSection.items.push({ type: 'numbered', ..._parseInline(content) });
        } else {
            const item = { type: 'paragraph', ..._parseInline(line) };
            if (currentSection) currentSection.items.push(item);
            else introParagraphs.push(item);
        }
    }
    if (introParagraphs.length && !sections.length) sections.push({ type: 'intro', heading: null, items: introParagraphs });
    if (currentSection) sections.push(currentSection);
    return sections;
}

function _parseInline(text) {
    const parts = [];
    const regex = /\*\*(.+?)\*\*/g;
    let last = 0, match;
    while ((match = regex.exec(text)) !== null) {
        if (match.index > last) parts.push({ bold: false, text: text.slice(last, match.index) });
        parts.push({ bold: true, text: match[1] });
        last = regex.lastIndex;
    }
    if (last < text.length) parts.push({ bold: false, text: text.slice(last) });
    return { parts, plainText: parts.map(p => p.text).join('') };
}

function _parseConfidence(score) {
    const value = parseFloat(score);
    let level, color;
    if (value >= 80)      { level = 'high';     color = '#2e7d32'; }
    else if (value >= 60) { level = 'moderate'; color = '#f57c00'; }
    else                  { level = 'low';      color = '#c62828'; }
    return { value, level, color };
}

function _escHTML(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function _capitalize(str) { return str.charAt(0).toUpperCase() + str.slice(1); }

function renderTreatment(el, ragInput) {
    el.innerHTML = renderRAGToHTML(formatRAGOutput(ragInput));
}


// ══════════════════════════════════════════
// ── GPS LOCATION DETECT ──
// ══════════════════════════════════════════

function detectScanLocation() {
    const btn    = document.getElementById('detect-location-btn');
    const label  = document.getElementById('detect-location-text');
    const coords = document.getElementById('location-coords');

    if (!navigator.geolocation) { alert('Geolocation is not supported by your browser.'); return; }

    btn.classList.remove('detected');
    btn.classList.add('detecting');
    btn.disabled      = true;
    label.textContent = 'Detecting…';

    navigator.geolocation.getCurrentPosition(
        pos => {
            const lat = pos.coords.latitude.toFixed(6);
            const lng = pos.coords.longitude.toFixed(6);
            locationLatInput.value = lat;
            locationLngInput.value = lng;
            btn.classList.remove('detecting');
            btn.classList.add('detected');
            btn.disabled         = false;
            label.textContent    = 'Location Detected ✓';
            coords.style.display = 'block';
            coords.textContent   = `${lat}, ${lng}`;
        },
        err => {
            btn.classList.remove('detecting');
            btn.disabled      = false;
            label.textContent = 'Detect My Location';
            const messages = { 1: 'Permission denied.', 2: 'Location unavailable.', 3: 'Request timed out.' };
            alert(messages[err.code] || 'Could not get location.');
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}


// ══════════════════════════════════════════
// ── LOCATION WARNING HELPERS ──
// ══════════════════════════════════════════

function showLocationWarning(msg) {
    let el = document.getElementById('location-warning');
    if (!el) {
        el = document.createElement('div');
        el.id = 'location-warning';
        el.style.cssText = 'color:#b45309;background:#fef3c7;border:1px solid #f59e0b;padding:8px 12px;border-radius:6px;font-size:13px;margin-top:8px';
        scanButton.parentNode.insertBefore(el, scanButton.nextSibling);
    }
    el.textContent   = '⚠️ ' + msg;
    el.style.display = 'block';
}

function hideLocationWarning() {
    const el = document.getElementById('location-warning');
    if (el) el.style.display = 'none';
}


// ══════════════════════════════════════════
// ── SCAN BUTTON ──
// ══════════════════════════════════════════

scanButton.addEventListener('click', async () => {
    if (fileInput.files.length === 0) { alert('Please upload an image first!'); return; }

    const selectedOption = fieldSelect.options[fieldSelect.selectedIndex];
    const fieldId   = fieldSelect.value;
    const fieldName = fieldId ? selectedOption.textContent : '—';

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('image', file);
    if (fieldId) formData.append('field_id', fieldId);

    statusText.textContent = 'Preparing…';
    statusText.style.color = 'orange';
    scanButton.disabled    = true;
    document.getElementById('btn-text').textContent = 'Processing...';
    resultCard.style.display = 'block';

    // Use pre-detected coords or fall back to auto-geolocation
    let lat = locationLatInput.value;
    let lng = locationLngInput.value;

    if (!lat || !lng) {
        statusText.textContent = 'Getting location...';
        const coords = await new Promise(resolve => {
            if (!navigator.geolocation) return resolve({ lat: '', lng: '' });
            const timer = setTimeout(() => {
                showLocationWarning('Location timed out — scan will proceed without coordinates.');
                resolve({ lat: '', lng: '' });
            }, 8000);
            navigator.geolocation.getCurrentPosition(
                pos => { clearTimeout(timer); hideLocationWarning(); resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }); },
                err => {
                    clearTimeout(timer);
                    const msgs = { 1: 'Location permission denied.', 2: 'Location unavailable.', 3: 'Location timed out.' };
                    showLocationWarning((msgs[err.code] || 'Location unavailable.') + ' Scan will proceed without coordinates.');
                    resolve({ lat: '', lng: '' });
                },
                { enableHighAccuracy: true, timeout: 5000, maximumAge: 30000 }
            );
        });
        lat = coords.lat;
        lng = coords.lng;
    }

    formData.append('latitude',  lat);
    formData.append('longitude', lng);
    formData.append('location',  (lat && lng) ? `${lat},${lng}` : '');
    formData.append('barcode',   barcodeInput.value.trim());

    statusText.textContent = 'Analyzing...';

    try {
        const response = await fetch('/analayze', { method: 'POST', body: formData });
        const result   = await response.json();
        console.log(result);

        if (response.ok) {
            const loc     = result.location || ((lat && lng) ? `${lat}, ${lng}` : '—');
            const barcode = result.barcode  || barcodeInput.value.trim() || '—';

            statusText.textContent     = result.status;
            statusText.style.color     = '#157f3c';
            confidenceText.textContent = result.confidence;
            renderTreatment(treatmentText, result.treatment);
            resultBadge.textContent    = result.status;
            resultField.textContent    = fieldName;
            resultBarcode.textContent  = barcode;

            // ── Severity ──
            const severityEl = document.getElementById('result-severity');
            const severityRaw = (result.severity_level || '—').toLowerCase();
            severityEl.innerHTML = '';
            if (severityRaw !== '—') {
                const badge = document.createElement('span');
                badge.className = `severity-badge ${severityRaw}`;
                badge.textContent = severityRaw.charAt(0).toUpperCase() + severityRaw.slice(1);
                severityEl.appendChild(badge);
            } else {
                severityEl.textContent = '—';
            }

            // ── Recovery — hide if status is 'new' ──
            const recoveryRow = document.getElementById('recovery-row');
            const recoveryEl  = document.getElementById('result-recovery');
            const detectionStatus = (result.detection_status || result.status || '').toLowerCase();
            if (detectionStatus === 'new') {
                recoveryRow.style.display = 'none';
            } else {
                recoveryRow.style.display = '';
                recoveryEl.textContent = result.recovery_percentage
                    ? result.recovery_percentage + '%'
                    : '—';
            }

            addToHistory({
                status:            result.status,
                confidence:        result.confidence,
                treatment:         result.treatment,
                field:             fieldName,
                location:          loc,
                barcode:           barcode,
                severity_level:    result.severity_level || '—',
                recovery_percentage: result.recovery_percentage || null,
                detection_status:  result.detection_status || result.status,
                imageDataUrl:      previewImg.src,
                date:              new Date().toLocaleString()
            });
        } else {
            statusText.textContent = 'Error during analysis';
            statusText.style.color = 'red';
            console.error(result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = 'Connection Failed';
        statusText.style.color = 'red';
    } finally {
        // Re-enable only if conditions still met
        checkScanReady();
        document.getElementById('btn-text').textContent = 'Start Analysis';
    }
});


// ══════════════════════════════════════════
// ── HISTORY ──
// ══════════════════════════════════════════

function addToHistory(entry) { analysisHistory.unshift(entry); renderHistory(); }

function renderHistory() {
    historyEmpty.style.display = analysisHistory.length === 0 ? 'flex' : 'none';
    historyCount.textContent   = `${analysisHistory.length} scan${analysisHistory.length !== 1 ? 's' : ''}`;
    historyList.querySelectorAll('.history-item').forEach(el => el.remove());

    analysisHistory.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'history-item';

        const svgLeaf = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>`;
        const svgPin  = `<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>`;
        const svgTag  = `<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2H2v10l9.29 9.29a1 1 0 0 0 1.41 0l7.29-7.29a1 1 0 0 0 0-1.41L12 2z"/><circle cx="7" cy="7" r="1.5" fill="currentColor" stroke="none"/></svg>`;

        item.innerHTML = `
            <div class="history-item-top">
                ${entry.imageDataUrl
                    ? `<img class="history-thumb" src="${entry.imageDataUrl}" alt="thumb">`
                    : `<div class="history-thumb-placeholder">${svgLeaf}</div>`}
                <div class="history-info">
                    <div class="history-status">${entry.status}</div>
                    <div class="history-confidence">${entry.confidence}</div>
                </div>
            </div>
            <div class="history-meta">
                ${entry.field    && entry.field    !== '—' ? `<span class="history-tag">${svgLeaf} ${entry.field}</span>`   : ''}
                ${entry.location && entry.location !== '—' ? `<span class="history-tag">${svgPin} ${entry.location}</span>` : ''}
                ${entry.barcode  && entry.barcode  !== '—' ? `<span class="history-tag">${svgTag} ${entry.barcode}</span>`  : ''}
            </div>
            <div class="history-date">${entry.date}</div>
        `;

        item.addEventListener('click', () => {
            statusText.textContent     = entry.status;
            statusText.style.color     = '#157f3c';
            confidenceText.textContent = entry.confidence;
            renderTreatment(treatmentText, entry.treatment);
            resultBadge.textContent    = entry.status;
            resultField.textContent    = entry.field    || '—';
            resultBarcode.textContent  = entry.barcode  || '—';

            // ── Severity ──
            const severityEl  = document.getElementById('result-severity');
            const severityRaw = (entry.severity_level || '—').toLowerCase();
            severityEl.innerHTML = '';
            if (severityRaw !== '—') {
                const badge = document.createElement('span');
                badge.className = `severity-badge ${severityRaw}`;
                badge.textContent = severityRaw.charAt(0).toUpperCase() + severityRaw.slice(1);
                severityEl.appendChild(badge);
            } else {
                severityEl.textContent = '—';
            }

            // ── Recovery ──
            const recoveryRow = document.getElementById('recovery-row');
            const recoveryEl  = document.getElementById('result-recovery');
            const dStatus = (entry.detection_status || '').toLowerCase();
            if (dStatus === 'new') {
                recoveryRow.style.display = 'none';
            } else {
                recoveryRow.style.display = '';
                recoveryEl.textContent = entry.recovery_percentage ? entry.recovery_percentage + '%' : '—';
            }

            resultCard.style.display   = 'block';
            enterHistoryView(entry.imageDataUrl);
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

const fieldsRowEl       = document.querySelector('.fields-row');
const scanBtnEl         = document.getElementById('scan-button');
const noFieldsWarningEl = document.getElementById('no-fields-warning');

function enterHistoryView(imageUrl) {
    dropZoneEl.style.display    = 'none';
    historyViewer.style.display = 'block';
    fieldsRowEl.style.display   = 'none';
    scanBtnEl.style.display     = 'none';
    if (noFieldsWarningEl) noFieldsWarningEl.style.display = 'none';
    if (imageUrl) {
        historyViewImg.src             = imageUrl;
        historyViewImg.style.display   = 'block';
        historyViewNoImg.style.display = 'none';
    } else {
        historyViewImg.style.display   = 'none';
        historyViewNoImg.style.display = 'flex';
    }
}

function exitHistoryView() {
    historyViewer.style.display = 'none';
    dropZoneEl.style.display    = 'block';
    fieldsRowEl.style.display   = '';
    scanBtnEl.style.display     = '';
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    resultCard.style.display = 'none';
}

newScanBtn.addEventListener('click', exitHistoryView);

clearHistoryBtn.addEventListener('click', () => {
    if (analysisHistory.length === 0) return;
    if (confirm('Clear all analysis history?')) { analysisHistory = []; renderHistory(); }
});


// ══════════════════════════════════════════
// ── LOAD HISTORY FROM DATABASE ──
// ══════════════════════════════════════════

function loadHistoryFromDB(records) {
    if (!Array.isArray(records) || records.length === 0) { renderHistory(); return; }
    analysisHistory = records.map(record => ({
        status:              record.disease_name      || 'Unknown',
        confidence:          record.confidence        || '--%',
        treatment:           record.treatment         || 'No treatment data available.',
        field:               record.field_name        || '—',
        location:            record.location          || '—',
        barcode:             record.barcode           || '—',
        imageDataUrl:        record.imageDataUrl      || null,
        date:                record.date              || '—',
        severity_level:      record.severity_level    || '—',
        recovery_percentage: record.recovery_percentage != null ? record.recovery_percentage : null,
        detection_status:    record.detection_status  || 'new',
    }));
    renderHistory();
}

// ── Init ──
renderHistory();
checkScanReady();