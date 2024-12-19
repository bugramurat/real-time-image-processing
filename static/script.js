// Helper Functions and Utility Functions
// Debounce function will perform only the last operation in a given time
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), delay);
    };
}

// Using canvas to shrink the image
async function resizeImage(file, maxWidth, maxHeight) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                let width = img.width;
                let height = img.height;

                const aspectRatio = Math.min(maxWidth / width, maxHeight / height);
                if (aspectRatio < 1) {
                    width = width * aspectRatio;
                    height = height * aspectRatio;
                }

                // Resize on Canvas
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob((blob) => {
                    resolve(blob);
                }, 'image/jpeg', 0.8); // 80% quality
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}

function prepareFormData(img) {
    const formData = new FormData();
    formData.append('image', img);
    formData.append('colorspace', sliders.colorspace.value);
    formData.append('grayscale', sliders.grayscale.checked ? 'on' : 'off');
    formData.append('brightness', sliders.brightness.value);
    formData.append('adaptive_threshold', sliders.adaptiveThreshold.value);
    formData.append('global_threshold', sliders.globalThreshold.value);
    formData.append('otsu_threshold', sliders.otsuThreshold.checked ? 'on' : 'off');
    formData.append('apply_hsv', sliders.applyHSVCheckbox.checked ? 'on' : 'off');
    formData.append('lower_hue', sliders.lowerHueSlider.value);
    formData.append('upper_hue', sliders.upperHueSlider.value);
    formData.append('contrast', sliders.contrast.value);
    formData.append('exposure', sliders.exposure.value);
    formData.append('shadows', sliders.shadows.value);
    formData.append('highlights', sliders.highlights.value);
    formData.append('sharpness', sliders.sharpness.value);
    formData.append('definition', sliders.definition.value);
    formData.append('blur', sliders.blur.value);
    formData.append('brilliance', sliders.brilliance.value);
    formData.append('hue', sliders.hue.value);
    formData.append('saturation', sliders.saturation.value);
    formData.append('vibrance', sliders.vibrance.value);
    return formData;
}

function savePreviousStates() {
    Object.values(sliders).forEach((slider) => {
        previousSliderStates[slider.id] = slider.disabled;
    });
    resetButtons.forEach((button) => {
        previousButtonStates[button.dataset.target] = button.disabled;
    });
}

function restorePreviousStates() {
    Object.values(sliders).forEach((slider) => {
        slider.disabled = previousSliderStates[slider.id];
    });
    resetButtons.forEach((button) => {
        const target = button.dataset.target;
        button.disabled = previousButtonStates[target];
    });
}

function toggleSlidersState(disabled) {
    Object.values(sliders).forEach((slider, index) => {
        const resetButton = resetButtons[index];
        slider.disabled = disabled;
        if (resetButton) {
            resetButton.disabled = disabled;
        }
    });
}

function setSliderState(group, disabled) {
    group.forEach(slider => {
        slider.disabled = disabled;
    });
}

function validateSlider(slider) {
    if (slider.value < slider.min || slider.value > slider.max) {
        alert(`${slider.id} has an invalid value!`);
        slider.value = slider.defaultValue;
    }
}

function showSuccessMessage(message) {
    feedbackMessage.textContent = message;
    feedbackMessage.className = 'success';
    feedbackMessage.style.display = 'block';

    setTimeout(() => {
        feedbackMessage.style.display = 'none';
    }, 3000);
}

function showErrorMessage(message) {
    feedbackMessage.textContent = message;
    feedbackMessage.className = 'error';
    feedbackMessage.style.display = 'block';

    setTimeout(() => {
        feedbackMessage.style.display = 'none';
    }, 3000);
}

function handleError(error, userMessage) {
    console.error(error); // Log for dev
    showErrorMessage(userMessage || 'An error occurred, please try again later.');
}

function disableDefaultBehavior(element, events) {
    events.forEach(eventType => element.addEventListener(eventType, (e) => e.preventDefault()));
}

// DOM Manipulation and Element Setup
const uploadForm = document.getElementById('upload-form');
const controls = document.getElementById('controls');
const preview = document.getElementById('preview');
const imageInput = document.getElementById('image');
const miniImage = document.createElement('img');
const uploadButton = document.getElementById('upload-button');
const downloadArrayButton = document.getElementById('download-array-button');
const downloadProcessedButton = document.getElementById('download-processed-button');
const resetButtons = document.querySelectorAll('.reset-button');
const feedbackMessage = document.getElementById('feedback-message');
const sliders = {
    adaptiveThreshold: document.getElementById('adaptive_threshold'),
    globalThreshold: document.getElementById('global_threshold'),
    otsuThreshold: document.getElementById('otsu_threshold'),
    applyHSVCheckbox: document.getElementById('apply_hsv'),
    lowerHueSlider: document.getElementById('lower_hue'),
    upperHueSlider: document.getElementById('upper_hue'),
    colorspace: document.getElementById('color-format'),
    grayscale: document.getElementById('grayscale'),
    brightness: document.getElementById('brightness'),
    contrast: document.getElementById('contrast'),
    exposure: document.getElementById('exposure'),
    shadows: document.getElementById('shadows'),
    highlights: document.getElementById('highlights'),
    sharpness: document.getElementById('sharpness'),
    definition: document.getElementById('definition'),
    blur: document.getElementById('blur'),
    brilliance: document.getElementById('brilliance'),
    hue: document.getElementById('hue'),
    saturation: document.getElementById('saturation'),
    vibrance: document.getElementById('vibrance')
};

miniImage.id = 'mini-img';
miniImage.src = preview.src;
document.body.appendChild(miniImage);
miniImage.style.display = 'none';

let clickCount = 0
let previousImage = null;
let resizedImage = null;
let previousSliderStates = {};
let previousButtonStates = {};

disableDefaultBehavior(preview, ['dragstart', 'contextmenu']);
disableDefaultBehavior(miniImage, ['dragstart', 'contextmenu']);

// Event Listeners
imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        previousImage = file
    }
})
window.addEventListener('scroll', () => {
    const imageRect = preview.getBoundingClientRect();

    if (imageRect.bottom < imageRect.height / 2) {
        miniImage.style.display = 'block';
    } else if (imageRect.bottom > imageRect.height / 2) {
        miniImage.style.display = 'none';
    }
});
sliders.applyHSVCheckbox.addEventListener('change', () => {
    const isChecked = sliders.applyHSVCheckbox.checked;
    sliders.lowerHueSlider.disabled = !isChecked;
    sliders.upperHueSlider.disabled = !isChecked;
    const resetButtonLower = document.querySelector(`.reset-button[data-target="${sliders.lowerHueSlider.id}"]`);
    const resetButtonUpper = document.querySelector(`.reset-button[data-target="${sliders.upperHueSlider.id}"]`);
    resetButtonLower.disabled = !isChecked || sliders.lowerHueSlider.value === sliders.lowerHueSlider.defaultValue
    resetButtonUpper.disabled = !isChecked || sliders.upperHueSlider.value === sliders.upperHueSlider.defaultValue

    sliders.grayscale.disabled = isChecked
    sliders.globalThreshold.disabled = isChecked
    sliders.adaptiveThreshold.disabled = isChecked
    sliders.otsuThreshold.disabled = isChecked
});
sliders.grayscale.addEventListener('change', updateHSVAvailability);
sliders.globalThreshold.addEventListener('input', updateHSVAvailability);
sliders.adaptiveThreshold.addEventListener('input', updateHSVAvailability);
sliders.otsuThreshold.addEventListener('change', updateHSVAvailability);
uploadForm.addEventListener('submit', async(e) => {
    e.preventDefault();
    const file = previousImage
    clickCount++;
    handleImageUpload(file, clickCount > 1);
});
resetButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const targetId = button.getAttribute('data-target');
        const slider = document.getElementById(targetId);
        const valueDisplay = document.getElementById(`${targetId}-value`);


        if (slider) {
            // Reset the slider
            slider.value = slider.defaultValue;

            // Update value
            if (valueDisplay) {
                valueDisplay.textContent = slider.defaultValue;
            }

            // Trigger if there is an effect attached to the slider
            slider.dispatchEvent(new Event('input'));

            if (!sliders.grayscale.checked && sliders.adaptiveThreshold.value == 0 && !sliders.otsuThreshold.checked && sliders.globalThreshold.value == '128') {
                sliders.applyHSVCheckbox.disabled = false;
            }
        }
    });
});
// Handle real-time adjustments
Object.values(sliders).forEach((input) => {
    const valueElement = document.getElementById(`${input.id}-value`);
    const resetButton = document.querySelector(`.reset-button[data-target="${input.id}"]`);

    input.addEventListener('input', () => {
        if (!resizedImage) return;

        if (valueElement) {
            valueElement.textContent = input.value;
        }
        if (resetButton) {
            resetButton.disabled = input.value === input.defaultValue;
        }
    });

    input.addEventListener('input', debounce(async() => {
        if (!resizedImage) return;

        downloadArrayButton.disabled = true;
        uploadButton.disabled = true;
        downloadProcessedButton.disabled = true;
        imageInput.disabled = true

        const formData = prepareFormData(resizedImage)

        const response = await fetch('/process', {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            throw new Error('Failed to fetch data from server');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        preview.src = url;
        miniImage.src = url

        downloadArrayButton.disabled = false;
        uploadButton.disabled = false;
        downloadProcessedButton.disabled = false;
        imageInput.disabled = false
    }, 600)); // 0.6 seconds
});
downloadProcessedButton.addEventListener('click', () => {
    handleDownload(downloadProcessedButton, '/process-original', 'processed-original-image.jpg');
});
downloadArrayButton.addEventListener('click', () => {
    handleDownload(downloadArrayButton, '/download-array', `${sliders.colorspace.value}-array.txt`);
});

// Main Functions
async function handleImageUpload(file, reset) {
    if (reset && !confirm("All settings will be reset, are you sure?")) {
        return;
    }
    if (!file) {
        handleError(null, 'Please select an image.');
        return;
    }

    setSliderState([sliders.lowerHueSlider, sliders.upperHueSlider], true);
    setSliderState([sliders.grayscale, sliders.globalThreshold, sliders.adaptiveThreshold, sliders.otsuThreshold, sliders.applyHSVCheckbox], false);
    resetSliders();

    try {
        resizedImage = await resizeImage(file, 1920, 1080);
        miniImage.src = URL.createObjectURL(resizedImage);

        const formData = prepareFormData(resizedImage);
        const response = await fetch('/process', { method: 'POST', body: formData });

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        preview.src = url;
        preview.style.display = 'block';
        controls.style.display = 'block';
        downloadArrayButton.style.display = 'block';
        downloadProcessedButton.style.display = 'inline-block';

        showSuccessMessage('Image uploaded.');
    } catch (error) {
        console.error('Error during image upload:', error);
        handleError(null, 'Error during image upload.');
    }
}

async function handleDownload(button, url, fileName) {
    button.disabled = true;
    let tempBtnName = button.textContent
    button.textContent = 'Processing...';
    savePreviousStates();
    toggleSlidersState(true);
    downloadArrayButton.disabled = true;
    uploadButton.disabled = true;
    downloadProcessedButton.disabled = true;
    imageInput.disabled = true

    const formData = prepareFormData(previousImage);
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            throw new Error('Failed to fetch data from server');
        }

        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(downloadUrl);

        showSuccessMessage('Download started.');
    } catch (error) {
        console.error('Download failed:', error);
        handleError(null, 'Download failed.');
    } finally {
        button.disabled = false;
        button.textContent = tempBtnName;
        restorePreviousStates();
        downloadArrayButton.disabled = false;
        uploadButton.disabled = false;
        downloadProcessedButton.disabled = false;
        imageInput.disabled = false
    }
}

function updateHSVAvailability() {
    const isDisabled = sliders.grayscale.checked ||
        sliders.globalThreshold.value !== '128' ||
        sliders.adaptiveThreshold.value !== '0' ||
        sliders.otsuThreshold.checked;
    sliders.applyHSVCheckbox.disabled = isDisabled;
}

function resetSliders() {
    Object.values(sliders).forEach((input) => {
        if (input.type === 'range') {
            input.value = input.defaultValue; // Reset the slider
            const valueElement = document.getElementById(`${input.id}-value`);
            const resetButton = document.querySelector(`.reset-button[data-target="${input.id}"]`);

            if (valueElement) {
                valueElement.textContent = input.defaultValue; // Reset the value
            }
            if (resetButton) {
                resetButton.disabled = input.value === input.defaultValue;
            }
        } else if (input.type === 'checkbox') {
            input.checked = input.defaultChecked;
        } else if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        }
    });
}