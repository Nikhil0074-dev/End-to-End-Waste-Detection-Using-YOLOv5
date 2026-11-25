const input = document.querySelector('#image-file');
const preview = document.querySelector('#preview');
const result = document.querySelector('#result');
const button = document.querySelector('#detect');
const status = document.querySelector('#status');
let selectedData = '';

input.addEventListener('change', () => {
  const file = input.files?.[0];
  result.hidden = true;
  selectedData = '';
  button.disabled = true;
  if (!file) return;
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 10 * 1024 * 1024) {
    status.textContent = 'Select a PNG, JPEG, or WebP image smaller than 10 MB.';
    input.value = '';
    return;
  }
  const reader = new FileReader();
  reader.onload = () => { selectedData = reader.result; preview.src = selectedData; preview.hidden = false; button.disabled = false; status.textContent = ''; };
  reader.onerror = () => { status.textContent = 'Could not read the selected image.'; };
  reader.readAsDataURL(file);
});

button.addEventListener('click', async () => {
  button.disabled = true;
  status.textContent = 'Running detection…';
  try {
    const response = await fetch('/predict', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({image: selectedData})});
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Detection failed.');
    result.src = `data:image/png;base64,${body.image}`;
    result.hidden = false;
    status.textContent = 'Detection complete.';
  } catch (error) { status.textContent = error.message || 'Unable to contact the detection service.'; }
  finally { button.disabled = false; }
});
