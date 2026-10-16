# Evidence screenshots

| File | Module | Shows |
|---|---|---|
| `01-app-browser.png` | M1 | App at http://localhost:3000 (docker compose) |
| `02-pytest.png` | M2 | `pytest -v`: 14 tests passing |
| `03-compose-up.png` | M4 | `docker compose up --build` with postgres, backend and frontend |
| `04-git-log.png` | M3 | `git log --oneline`: 20 commits |
| `05-actions-green.png` | M5 | Green run: test, terraform, build/Trivy/push, deploy |
| `06-trivy.png` | M6 | Trivy scan: 0 HIGH/CRITICAL |
| `06b-trivy-blocked.png` | M6 | Run #1 blocked by Trivy (HIGH CVEs, exit code 1, push skipped) |
| `07-ghcr.png` | M5 | GHCR package with images tagged by commit SHA |
| `08-terraform-plan.png` | M7 | `terraform plan`: 58 to add |
| `08b-terraform-apply.png` | M7 | `terraform apply` complete |
| `09a-aws-vpc.png` | M7 | VPC `stockpilot-dev-vpc` in ap-south-1 |
| `09b-aws-subnets.png` | M7 | 2 public and 2 private subnets |
| `09c-aws-eks.png` | M7 | EKS cluster `stockpilot-eks` Active |
| `09d-aws-nodegroup.png` | M7 | Managed node group `main` Active |
| `09e-eks-nodes.png` | M7 | `kubectl get nodes` on EKS: 2 Ready |
| `10-terraform-destroy.png` | M7 | `terraform destroy`: 58 destroyed |
| `11-kubernetes-helm.png` | M8 | Pods (2 backend, 2 frontend, postgres), services, ingress, HPA, `helm list` |
| `14-ingress-browser.png` | M8 | App via Ingress at http://stockpilot.local |
| `15-hpa.png` | M8 | HPA scaling the backend from 2 to 4 pods under load |
| `16-metrics.png` | M9 | Backend `/metrics` endpoint |
| `17-prometheus-targets.png` | M9 | Prometheus targets: stockpilot-backend 6/6 UP |
| `18-grafana.png` | M9 | Grafana "StockPilot API" dashboard with live traffic and HPA pods |
