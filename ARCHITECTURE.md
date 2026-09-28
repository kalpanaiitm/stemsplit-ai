# Architecture

FastAPI upload → bounded file → synchronous Demucs subprocess → stem downloads and ZIP.

The README names the runnable entry point. Components should keep validation separate from the core operation and presentation. The existing code is the source of truth; this page does not claim planned capabilities as implemented.

## Failure and privacy boundaries
Demucs performs inference; orchestration is synchronous, CPU/GPU intensive, and outputs remain on disk. Use non-sensitive or permitted inputs for demos. Do not commit user documents, audio, credentials, or generated outputs.
