from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import uuid
import shutil
import zipfile

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_SUFFIXES = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
MAX_BYTES = 50 * 1024 * 1024

app = FastAPI(title="StemSplit AI API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down to the production website domain later
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def home():
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Web interface not found")
    return FileResponse(index, media_type="text/html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/separate")
async def separate(file: UploadFile = File(...)):
    suffix = Path(file.filename or "audio.wav").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Unsupported audio format")

    job_id = uuid.uuid4().hex
    job_upload = UPLOAD_DIR / f"{job_id}{suffix}"
    job_output = OUTPUT_DIR / job_id
    job_output.mkdir(parents=True, exist_ok=True)

    size = 0
    with job_upload.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_BYTES:
                f.close()
                job_upload.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large. Max 50 MB for MVP.")
            f.write(chunk)

    cmd = [
        "python", "-m", "demucs.separate",
        "-n", "htdemucs_6s",
        "-o", str(job_output),
        str(job_upload),
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        shutil.rmtree(job_output, ignore_errors=True)
        job_upload.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Separation failed: {e.stderr[-500:]}")

    stem_root = job_output / "htdemucs_6s" / job_upload.stem
    stems = {}
    for stem in ["vocals", "drums", "bass", "guitar", "piano", "other"]:
        path = stem_root / f"{stem}.wav"
        if path.exists():
            stems[stem] = f"/jobs/{job_id}/{stem}"

    job_upload.unlink(missing_ok=True)

    if not stems:
        raise HTTPException(status_code=500, detail="No stems were produced")

    return {"job_id": job_id, "stems": stems}

@app.get("/jobs/{job_id}/{stem}")
def get_stem(job_id: str, stem: str):
    if stem not in {"vocals", "drums", "bass", "guitar", "piano", "other"}:
        raise HTTPException(status_code=404, detail="Unknown stem")

    job_output = OUTPUT_DIR / job_id / "htdemucs_6s"
    candidates = list(job_output.glob(f"*/{stem}.wav"))
    if not candidates:
        raise HTTPException(status_code=404, detail="Stem not found")

    return FileResponse(
        candidates[0],
        media_type="audio/wav",
        filename=f"{stem}.wav",
    )
@app.get("/jobs/{job_id}/download-all")
def download_all_stems(job_id: str):
    job_dir = OUTPUT_DIR / job_id / "htdemucs_6s"

    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    zip_path = OUTPUT_DIR / f"{job_id}-stems.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for stem in ["vocals", "drums", "bass", "guitar", "piano", "other"]:
            stem_file = job_dir / f"{stem}.wav"

            if stem_file.exists():
                zip_file.write(stem_file, arcname=f"{stem}.wav")

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="stemsplit-all-stems.zip"
    )