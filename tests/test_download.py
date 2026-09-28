from pathlib import Path
from fastapi.testclient import TestClient
from app import main

def test_zip_contains_stems_in_demucs_output_layout(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path)
    job_id = "a" * 32
    stem_dir = tmp_path / job_id / "htdemucs_6s" / "track"
    stem_dir.mkdir(parents=True)
    (stem_dir / "vocals.wav").write_bytes(b"audio")
    response = TestClient(main.app).get(f"/jobs/{job_id}/download-all")
    assert response.status_code == 200
    from io import BytesIO
    from zipfile import ZipFile
    with ZipFile(BytesIO(response.content)) as archive:
        assert archive.namelist() == ["vocals.wav"]

def test_invalid_job_id_is_rejected():
    assert TestClient(main.app).get("/jobs/../download-all").status_code in (400, 404)
    assert TestClient(main.app).get("/jobs/not-a-job/download-all").status_code == 404
