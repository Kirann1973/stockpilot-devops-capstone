# Troubleshooting labs

| Lab | Symptom | Commands | Root cause |
|---|---|---|---|
| `broken-image.yaml` | Pod stuck in `ImagePullBackOff` | `kubectl describe pod`, `kubectl get events --sort-by=.lastTimestamp` | Image tag does not exist in GHCR |
| `broken-service.yaml` | Service has no endpoints, requests time out | `kubectl get endpoints`, `kubectl get pods --show-labels` | Selector label and targetPort don't match the backend Pods |
