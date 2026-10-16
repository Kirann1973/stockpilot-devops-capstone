# Trivy security scan

**What is scanned.** In the `build-scan-push` job, Trivy scans both freshly built images (`stockpilot-backend` on `python:3.12-slim`, `stockpilot-frontend` on `nginx-unprivileged:1.29-alpine`). It checks OS packages (Debian / Alpine) and language dependencies (the Python packages in the backend image) against public CVE databases.

**Gate.** `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`: the job fails, and nothing is pushed to GHCR, if any HIGH or CRITICAL vulnerability with an available fix is found. Unfixed CVEs are reported but don't block, because there is no upgrade to apply yet.

**Result.**
- **Run #1 was blocked.** Trivy found 7 fixable HIGH CVEs in the backend image: in starlette 0.46.2 (pulled in by FastAPI), urllib3 2.7.0, setuptools 70.3.0 and msgpack 1.1.2. Trivy exited with code 1, so the frontend scan, the GHCR login and the push were all skipped. No vulnerable image was published (`docs/screenshots/06b-trivy-blocked.png`).
- **The fix.**
  - Upgraded FastAPI, which pulls in a patched Starlette.
  - Removed `pip`, `setuptools` and `wheel` from the runtime image, since the app doesn't need them at runtime.
  - Ran `apk upgrade` in the frontend Nginx image.
- **Runs #2 to #4 were clean.** Both images reported 0 HIGH/CRITICAL fixable vulnerabilities, so they were pushed to GHCR tagged with the commit SHA (`docs/screenshots/06-trivy.png`).

A clean scan means there were no known, fixable high-risk CVEs in the OS packages or Python libraries at scan time. It does not prove the app is secure. Code analysis (SAST), secret scanning and runtime security are separate layers.
