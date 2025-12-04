// Image Upload Handling
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('image');
    const previewSection = document.getElementById('preview-section');
    const imagePreview = document.getElementById('image-preview');
    const removeBtn = document.getElementById('remove-image');
    const toggleAdvancedBtn = document.getElementById('toggle-advanced');
    const advancedSettings = document.getElementById('advanced-settings');
    const toggleIcon = document.getElementById('toggle-icon');

    // Mode Options Toggle
    window.toggleModeOptions = function() {
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const embodimentSection = document.getElementById('embodiment-selection');

        // All modes require images now
        // Show embodiment selection only for embodiment mode
        if (mode === 'embodiment') {
            if (embodimentSection) embodimentSection.style.display = 'block';
        } else {
            if (embodimentSection) embodimentSection.style.display = 'none';
        }
    };

    // Legacy function for compatibility
    window.toggleImageUpload = window.toggleModeOptions;

    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Handle file selection
    function handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            return;
        }

        if (file.size > 20 * 1024 * 1024) {
            alert('File size must be less than 20MB');
            return;
        }

        // Preview image
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZone.style.display = 'none';
            previewSection.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    // Remove image
    removeBtn.addEventListener('click', () => {
        resetImageUpload();
    });

    function resetImageUpload() {
        fileInput.value = '';
        imagePreview.src = '';
        dropZone.style.display = 'block';
        previewSection.classList.add('hidden');
    }

    // Advanced settings toggle
    if (toggleAdvancedBtn) {
        toggleAdvancedBtn.addEventListener('click', () => {
            const isHidden = advancedSettings.style.display === 'none';
            advancedSettings.style.display = isHidden ? 'block' : 'none';
            toggleIcon.textContent = isHidden ? '−' : '+';
        });
    }

    // Form validation
    const form = document.querySelector('.generation-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const prompt = document.getElementById('prompt').value.trim();

            if (!prompt) {
                e.preventDefault();
                alert('Please enter a task description');
                return;
            }

            // All modes require images now (image2world only)
            if (!fileInput.files.length) {
                e.preventDefault();
                alert('Please upload an image (all modes require images)');
                return;
            }

            // Show loading indicator
            const submitBtn = form.querySelector('.submit-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Processing...';
        });
    }

    // Initialize
    toggleImageUpload();
});
