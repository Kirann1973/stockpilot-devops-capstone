# Trivy security scan

**What is scanned.** In the `build-scan-push` job, Trivy scans both freshly built images (`stockpilot-backend` on `python:3.12-slim`, `stockpilot-frontend` on `nginx-unprivileged:1.29-alpine`). It checks OS packages (Debian / Alpine) and language dependencies (the Python packages in the backend image) against public CVE databases.

**Gate.** `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`: the job fails, and nothing is pushed to GHCR, if any HIGH or CRITICAL vulnerability with an available fix is found. Unfixed CVEs are reported but don't block, because there is no upgrade to apply yet.

**Result.** _Fill in after the pipeline run, e.g.:_ "The scan of both images reported 0 HIGH/CRITICAL fixable vulnerabilities, so the images were pushed. A clean scan means no known fixable high-risk CVEs in the base OS packages or Python libraries at scan time. It does not prove the app is secure: SAST, secret scanning and runtime security are separate layers."
