# Test report

## Scope
This report distinguishes automated tests from an end-to-end or deployed demonstration. A passing unit test does not prove model quality, document fidelity, or deployment reliability.

## Current verification
See the tests and workflow (if present) in this repository. Local run on 2026-09-28: `python -m pytest -q` → **2 passed in 0.25s**. This is a local unit/component result; a deployed end-to-end check has not been performed.

## Remaining evaluation
Mocked endpoint tests, input failure handling, output expiry and measured processing time.

The first ZIP test failed with HTTP 404. Root cause: the dynamic stem route intercepted `download-all`. The route now dispatches the fixed path; the failed test and the suite were rerun and passed. Demucs itself was not run in this test.
