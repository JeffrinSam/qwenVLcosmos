/**
 * Cosmos Predict 2.5 - Simple Web Interface
 * Frontend JavaScript for handling image upload, form validation, and submission
 */

// Global state
let uploadedFile = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeDropZone();
    initializeForm();
    initializeAutoregressiveToggle();
    initializeResolutionSelector();
});

/**
 * Initialize drag & drop zone for image upload
 */
function initializeDropZone() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('image-upload');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-image');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, false);

    // Handle click to browse
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Handle remove button
    removeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        clearImage();
    });
}

/**
 * Prevent default drag and drop behavior
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Handle file upload and validation
 */
function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Invalid file type. Please upload a JPG, PNG, or WEBP image.');
        return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
        alert('File is too large. Maximum size is 50MB.');
        return;
    }

    // Store file
    uploadedFile = file;

    // Update file input
    const fileInput = document.getElementById('image-upload');
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;

    // Show preview
    showPreview(file);
}

/**
 * Display image preview
 */
function showPreview(file) {
    const dropZone = document.getElementById('drop-zone');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');

    const reader = new FileReader();

    reader.onload = function(e) {
        imagePreview.src = e.target.result;
        dropZone.style.display = 'none';
        previewContainer.style.display = 'block';
    };

    reader.readAsDataURL(file);
}

/**
 * Clear uploaded image
 */
function clearImage() {
    const dropZone = document.getElementById('drop-zone');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const fileInput = document.getElementById('image-upload');

    uploadedFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    previewContainer.style.display = 'none';
    dropZone.style.display = 'block';
}

/**
 * Initialize form submission
 */
function initializeForm() {
    const form = document.getElementById('generate-form');
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const submitSpinner = document.getElementById('submit-spinner');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validate image is uploaded
        const fileInput = document.getElementById('image-upload');
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please upload an image first.');
            return;
        }

        // Validate prompt
        const prompt = document.getElementById('prompt').value.trim();
        if (!prompt) {
            alert('Please enter a prompt.');
            return;
        }

        // Validate numeric fields
        if (!validateNumericFields()) {
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitText.textContent = 'Submitting...';
        submitSpinner.style.display = 'inline-block';

        try {
            // Create FormData from form
            const formData = new FormData(form);

            // Submit to server
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.job_id) {
                // Redirect to status page
                window.location.href = `/status/${data.job_id}`;
            } else {
                // Show error
                alert('Error: ' + (data.error || 'Unknown error occurred'));
                resetSubmitButton(submitBtn, submitText, submitSpinner);
            }
        } catch (error) {
            console.error('Error submitting job:', error);
            alert('Error submitting job: ' + error.message);
            resetSubmitButton(submitBtn, submitText, submitSpinner);
        }
    });
}

/**
 * Validate numeric form fields
 */
function validateNumericFields() {
    const fields = [
        { id: 'num_output_frames', name: 'Number of Output Frames', min: 1, max: 1000 },
        { id: 'chunk_size', name: 'Chunk Size', min: 1, max: 200 },
        { id: 'chunk_overlap', name: 'Chunk Overlap', min: 0, max: 10 },
        { id: 'resolution_height', name: 'Resolution Height', min: 128, max: 1080 },
        { id: 'resolution_width', name: 'Resolution Width', min: 128, max: 1920 },
        { id: 'seed', name: 'Seed', min: 0, max: 2147483647 },
        { id: 'guidance', name: 'Guidance', min: 0, max: 7 }
    ];

    for (const field of fields) {
        const element = document.getElementById(field.id);
        const value = parseInt(element.value);

        if (isNaN(value)) {
            alert(`${field.name} must be a valid number.`);
            element.focus();
            return false;
        }

        if (value < field.min || value > field.max) {
            alert(`${field.name} must be between ${field.min} and ${field.max}.`);
            element.focus();
            return false;
        }
    }

    return true;
}

/**
 * Reset submit button to normal state
 */
function resetSubmitButton(submitBtn, submitText, submitSpinner) {
    submitBtn.disabled = false;
    submitText.textContent = 'Generate Video';
    submitSpinner.style.display = 'none';
}

/**
 * Initialize autoregressive mode toggle
 */
function initializeAutoregressiveToggle() {
    const autoCheckbox = document.getElementById('enable_autoregressive');
    const chunkSettings = document.getElementById('chunk-settings');

    // Set initial state
    updateChunkSettingsVisibility();

    // Add event listener
    autoCheckbox.addEventListener('change', updateChunkSettingsVisibility);

    function updateChunkSettingsVisibility() {
        if (autoCheckbox.checked) {
            chunkSettings.style.display = 'block';
        } else {
            chunkSettings.style.display = 'none';
        }
    }
}

/**
 * Initialize resolution preset selector
 */
function initializeResolutionSelector() {
    const resolutionPreset = document.getElementById('resolution_preset');
    const customResolution = document.getElementById('custom-resolution');
    const resolutionHeight = document.getElementById('resolution_height');
    const resolutionWidth = document.getElementById('resolution_width');

    // Set initial state
    updateResolutionFields();

    // Add event listener
    resolutionPreset.addEventListener('change', updateResolutionFields);

    function updateResolutionFields() {
        const selectedValue = resolutionPreset.value;

        if (selectedValue === 'custom') {
            // Show custom resolution fields
            customResolution.style.display = 'grid';
        } else {
            // Hide custom fields and update from preset
            customResolution.style.display = 'none';

            // Parse preset value (format: "height,width")
            const [height, width] = selectedValue.split(',');
            resolutionHeight.value = height;
            resolutionWidth.value = width;
        }
    }
}

/**
 * Utility: Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Utility: Validate image file
 */
function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    return validTypes.includes(file.type);
}
