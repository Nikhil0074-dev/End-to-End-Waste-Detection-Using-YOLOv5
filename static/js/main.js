const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const chuteInner = document.getElementById("chuteInner");
const previewImg = document.getElementById("previewImg");
const scanBtn = document.getElementById("scanBtn");
const statusTag = document.getElementById("statusTag");
const resultPanel = document.getElementById("resultPanel");
const resultImg = document.getElementById("resultImg");
const trainBtn = document.getElementById("trainBtn");
const trainStatus = document.getElementById("trainStatus");

let base64Image = null;

function setStatus(text, kind) {
  statusTag.textContent = text;
  statusTag.className = "status-tag" + (kind ? " " + kind : "");
}

function handleFile(file) {
  if (!file || !file.type.startsWith("image/")) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    base64Image = e.target.result.split(",")[1];
    previewImg.src = e.target.result;
    previewImg.hidden = false;
    chuteInner.hidden = true;
    scanBtn.disabled = false;
    setStatus("ready");
    resultPanel.hidden = true;
  };
  reader.readAsDataURL(file);
}

dropzone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => handleFile(e.target.files[0]));

["dragenter", "dragover"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
  })
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  handleFile(file);
});

scanBtn.addEventListener("click", async () => {
  if (!base64Image) return;
  setStatus("scanning…", "busy");
  scanBtn.disabled = true;
  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: base64Image }),
    });
    if (!res.ok) throw new Error(`Server responded ${res.status}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    resultImg.src = "data:image/jpeg;base64," + data.image;
    resultPanel.hidden = false;
    setStatus("done", "ok");
  } catch (err) {
    console.error(err);
    setStatus("failed", "err");
  } finally {
    scanBtn.disabled = false;
  }
});

trainBtn.addEventListener("click", async () => {
  trainStatus.textContent = "training…";
  trainBtn.disabled = true;
  try {
    const res = await fetch("/train");
    const text = await res.text();
    trainStatus.textContent = res.ok ? "training complete" : "training failed";
    console.log(text);
  } catch (err) {
    trainStatus.textContent = "training failed";
  } finally {
    trainBtn.disabled = false;
  }
});
