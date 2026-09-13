# StemSplit AI

Website-ready FastAPI backend for separating an uploaded song into stems.

## MVP stems
- vocals
- drums
- bass
- guitar
- piano
- other

The backend uses Demucs `htdemucs_6s`.

## Local setup

### 1. Install system dependency
Install FFmpeg and make sure `ffmpeg` is available on PATH.

### 2. Create a virtual environment
```bash
python -m venv .venv
```

Activate it, then install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Website integration
Send a multipart POST request to `/separate` with field name `file`.

Example JavaScript:
```html
<input id="song" type="file" accept="audio/*" />
<button onclick="separateSong()">Separate</button>
<div id="results"></div>

<script>
const API_BASE = "https://YOUR-API-DOMAIN";

async function separateSong() {
  const input = document.getElementById("song");
  if (!input.files.length) return;

  const form = new FormData();
  form.append("file", input.files[0]);

  const response = await fetch(`${API_BASE}/separate`, {
    method: "POST",
    body: form
  });

  if (!response.ok) {
    alert("Separation failed");
    return;
  }

  const data = await response.json();
  const results = document.getElementById("results");
  results.innerHTML = "";

  for (const [name, path] of Object.entries(data.stems)) {
    const url = `${API_BASE}${path}`;
    results.innerHTML += `
      <h3>${name}</h3>
      <audio controls src="${url}"></audio>
      <a href="${url}" download>Download</a>
    `;
  }
}
</script>
```

## Important production notes

This MVP processes audio synchronously. That is fine for local testing, but production should use a background job queue because separation can take significant time.

Recommended production architecture:

Website → FastAPI → Job queue → GPU worker → object storage → signed download URLs

Before public launch also add:
- authentication or rate limiting
- strict allowed website origins for CORS
- storage expiry / automatic deletion
- max duration and file-size limits
- malware/file validation
- job status endpoint
- GPU hosting
- privacy and copyright terms

## Privacy
The MVP writes temporary uploads and generated stems to disk. Uploaded source files are deleted after separation. Generated stems remain until manually removed. Add automatic expiry before public deployment.
