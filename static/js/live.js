const video = document.getElementById("video");
const liveResult = document.getElementById("liveResult");
const camToggle = document.getElementById("camToggle");
const liveStatus = document.getElementById("liveStatus");

let stream = null;
let intervalId = null;

function setStatus(text, kind) {
  liveStatus.textContent = text;
  liveStatus.className = "status-tag" + (kind ? " " + kind : "");
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.hidden = false;
    liveResult.hidden = true;
    camToggle.textContent = "Stop camera";
    setStatus("streaming", "ok");

    const canvas = document.createElement("canvas");
    intervalId = setInterval(async () => {
      if (!video.videoWidth) return;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
      const base64Image = dataUrl.split(",")[1];

      try {
        const res = await fetch("/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: base64Image }),
        });
        const data = await res.json();
        if (data.image) {
          liveResult.src = "data:image/jpeg;base64," + data.image;
          liveResult.hidden = false;
        }
      } catch (err) {
        console.error("prediction failed", err);
      }
    }, 2000);
  } catch (err) {
    setStatus("camera denied", "err");
  }
}

function stopCamera() {
  if (stream) stream.getTracks().forEach((t) => t.stop());
  if (intervalId) clearInterval(intervalId);
  video.hidden = true;
  camToggle.textContent = "Start camera";
  setStatus("idle");
}

camToggle.addEventListener("click", () => {
  if (stream) {
    stopCamera();
  } else {
    startCamera();
  }
});
