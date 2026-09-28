# Project blueprint — stemsplit-ai

## Problem and scope
Musicians separating permitted audio for local experiments. The current repository scope is described by its README and implemented files.

## Architecture and contracts
FastAPI upload → bounded file → synchronous Demucs subprocess → stem downloads and ZIP. User content is untrusted data. Errors should be shown without disclosing private contents.

## Ground truth and review
Outputs must be checked against the input document, audio, or user-supplied evidence. No automated score proves scientific correctness or job suitability.

## Known limits
Demucs performs inference; orchestration is synchronous, CPU/GPU intensive, and outputs remain on disk.

## Next milestone and acceptance
Mocked endpoint tests, input failure handling, output expiry and measured processing time. The milestone is complete only when its implementation, meaningful tests, and measured results are committed.

## Release gate
Run automated tests, inspect realistic end-to-end output, record actual failures and limitations, and update the README before claiming the milestone.
