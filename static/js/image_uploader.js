// Get the button and result elements from your HTML
const scanButton = document.getElementById('scan-button');
const statusText = document.getElementById('status-text');
const confidenceText = document.getElementById('confidence-text');
const treatmentText = document.getElementById('treatment-text');

scanButton.addEventListener('click', async () => {
    // 1. Check if a file was actually selected
    if (fileInput.files.length === 0) {
        alert("Please upload an image first!");
        return;
    }

    // 2. Prepare the file to be sent
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('image', file);

    // Update UI to show it's loading
    statusText.textContent = "Analyzing...";
    statusText.style.color = "orange";
    scanButton.disabled = true; 
    scanButton.textContent = "Processing...";

    try {
        // 3. Send the POST request to your Flask route
        const response = await fetch('/analayze', {
            method: 'POST',
            body: formData 
        });

        const result = await response.json();
        console.log(result); 

        if (response.ok) {
            // 4. Update the UI with the results from Flask
            statusText.textContent = result.status;
            statusText.style.color = "green";
            confidenceText.textContent = result.confidence;
            treatmentText.textContent = result.treatment;
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
        // Reset the button state
        scanButton.disabled = false;
        scanButton.textContent = "Start Analysis";
    }
});