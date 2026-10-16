# StockPilot: Inventory Management on a Full DevOps Pipeline

**Student:** Kiran · **Roll No.:** 10446 · DevOps Final Capstone (Session 21)

StockPilot is a small, SaaS-style inventory management app. A store or office team uses it to:

- keep a catalogue of products (SKU, category, supplier, unit price)
- receive and ship stock with one click (`+10` / `−`)
- see stock status at a glance: **In stock**, **Low stock** (at or below the reorder level), **Out of stock**
- see KPIs: product count, units on hand, total inventory value, low-stock and out-of-stock counts
- filter by search text, category, or "needs reorder"

The DevOps layer shows how that app travels from a laptop to a monitored Kubernetes cluster.

```text
Developer ── git push ──► GitHub
                            │
                            ▼
                   GitHub Actions (.github/workflows/ci-cd.yml)
                   ├─ pytest (14 tests, SQLite test DB)
                   ├─ React build
                   ├─ terraform fmt + validate
                   ├─ docker build backend + frontend
                   ├─ Trivy scan (fails on HIGH/CRITICAL)
                   └─ push to GHCR, tag = commit SHA
                            │
          Terraform ──► AWS VPC (2 public + 2 private subnets) + EKS
                            │
                         Helm chart (helm/stockpilot)
                            │
          Ingress ── /      ──► frontend (React on Nginx, 2 replicas)
                  └─ /api   ──► backend  (FastAPI, 2+ replicas, HPA) ──► PostgreSQL (StatefulSet + PVC)
                            │
          Prometheus (ServiceMonitor scrapes /metrics) ──► Grafana dashboard "StockPilot API"
```

## Tech stack

| Layer | Tooling |
|---|---|
| Frontend | React 18 + Vite, responsive CSS, served by unprivileged Nginx |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic |
| Database | PostgreSQL 16 |
| Tests | Pytest + FastAPI TestClient on an isolated SQLite database |
| Containers | Docker (non-root images), Docker Compose |
| CI/CD | GitHub Actions → GHCR |
| Security | Trivy image scanning |
| IaC | Terraform (`terraform-aws-modules` VPC + EKS), region `ap-south-1` |
| Orchestration | Kubernetes, Helm, NGINX Ingress, HPA |
| Observability | Prometheus (kube-prometheus-stack), Grafana |

## Repository layout

```text
.
├── backend/                 FastAPI app
│   ├── app/                 main.py (routes), models.py, schemas.py, db.py, config.py
│   ├── alembic/versions/    0001 create products, 0002 seed demo data
│   ├── tests/               conftest.py + 14 pytest tests
│   ├── Dockerfile           non-root (uid 10001), runs migrations then uvicorn
│   └── requirements*.txt
├── frontend/                React + Vite app
│   ├── src/                 App.jsx, ProductModal.jsx, api.js, styles.css
│   ├── nginx.conf.template  serves the SPA and proxies /api to the backend
│   └── Dockerfile           multi-stage: node build → nginx-unprivileged (uid 101)
├── docker-compose.yml       postgres + backend + frontend
├── .github/workflows/       ci-cd.yml
├── terraform/               VPC + EKS, terraform.tfvars.example
├── k8s/namespace.yaml
├── helm/stockpilot/         Chart.yaml, values.yaml, templates/, dashboards/
├── monitoring/              kube-prometheus-stack values
├── troubleshooting/         broken-image and broken-service labs
├── scripts/load-test.sh     traffic generator for Grafana/HPA
└── docs/                    Trivy notes and screenshots
```

## REST API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (checks the database) |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/products?q=&category=&low_stock=` | List and filter products |
| GET | `/api/products/{id}` | One product |
| POST | `/api/products` | Create a product (409 on duplicate SKU) |
| PUT | `/api/products/{id}` | Update a product |
| POST | `/api/products/{id}/adjust` | Receive (+) or ship (−) stock |
| DELETE | `/api/products/{id}` | Delete a product |
| GET | `/api/products/stats` | Dashboard KPIs |

Swagger UI: `http://localhost:8000/docs`.

---

# How to run everything (step by step)

## 0. Tools to install

Git, Docker Desktop, kubectl, Helm 3, Minikube, Terraform ≥ 1.6, AWS CLI v2.

## 1. Run locally with Docker Compose

```bash
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health / metrics: http://localhost:8000/health, http://localhost:8000/metrics

Stop with `docker compose down` (add `-v` to wipe the database).

## 2. Run the tests

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -v
```

Tests set `DATABASE_URL=sqlite:///./test_stockpilot.db` in `tests/conftest.py` and recreate the schema for every test, so they never touch PostgreSQL.

## 3. CI/CD

Every push to `main` runs `.github/workflows/ci-cd.yml`:

1. **test**: pytest (fails the pipeline on any failure) and `npm run build`
2. **terraform**: `fmt -check`, `init -backend=false`, `validate`
3. **build-scan-push**: build both images, Trivy scan both (exit code 1 on HIGH/CRITICAL fixable CVEs), push to `ghcr.io/kirann1973/stockpilot-backend:<sha>` and `ghcr.io/kirann1973/stockpilot-frontend:<sha>`
4. **deploy**: `helm upgrade --install` with `image.tag=<sha>`. Runs only when a `KUBE_CONFIG_DATA` secret (base64 kubeconfig) is set; otherwise it is skipped with a notice.

Images live under the GitHub profile → **Packages**. If a package shows as private, open it → *Package settings* → *Change visibility* → Public, so the cluster can pull it without credentials.

## 4. Terraform: AWS VPC + EKS

```bash
aws configure                              # region ap-south-1
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan                             # screenshot
terraform apply                            # ~15-20 min
aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks
kubectl get nodes
# ... screenshots of VPC + EKS in the AWS console ...
terraform destroy                          # screenshot, ~10-15 min
```

Cost while running is about $0.25–0.30/hour. Destroy the same day.

## 5. Kubernetes + Helm (Minikube)

```bash
minikube start --cpus 4 --memory 6g
minikube addons enable ingress
minikube addons enable metrics-server

# monitoring first, so the ServiceMonitor CRD exists
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/kube-prometheus-stack-values.yaml

kubectl apply -f k8s/namespace.yaml
export TAG=<full commit SHA from a green pipeline run>
helm upgrade --install stockpilot ./helm/stockpilot -n stockpilot \
  -f helm/stockpilot/values-minikube.yaml --set image.tag=$TAG

kubectl get pods -n stockpilot            # all Running, 2 backend + 2 frontend + postgres
kubectl get svc -n stockpilot
kubectl get ingress,hpa -n stockpilot
helm list -n stockpilot
```

Open through the Ingress:

- **Linux:** add `$(minikube ip) stockpilot.local` to `/etc/hosts`, then open http://stockpilot.local
- **macOS / Windows (Docker driver):** run `minikube tunnel` in a separate terminal, add `127.0.0.1 stockpilot.local` to the hosts file, then open http://stockpilot.local

## 6. HPA demo

```bash
URL=http://stockpilot.local ./scripts/load-test.sh 5000 40
kubectl get hpa -n stockpilot -w
```

## 7. Prometheus + Grafana

```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090
# http://localhost:9090/targets → stockpilot-backend UP

kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
# http://localhost:3001  (admin / stockpilot-admin) → Dashboards → "StockPilot API"
```

## 8. Troubleshooting labs

See [troubleshooting/README.md](troubleshooting/README.md): a deployment with a non-existent image tag (`ImagePullBackOff`) and a Service whose selector matches no Pods.

## 9. Live demo flow

1. Change something visible, e.g. the subtitle in `frontend/src/App.jsx`.
2. `git commit -am "Update dashboard subtitle" && git push`.
3. Show the pipeline: tests → Trivy → images in GHCR with the new SHA.
4. `helm upgrade --install stockpilot ./helm/stockpilot -n stockpilot -f helm/stockpilot/values-minikube.yaml --set image.tag=<new sha>`.
5. `kubectl rollout status deploy/stockpilot-frontend -n stockpilot`, then refresh the browser.

## Security notes

- No credentials are committed. `.env`, `*.tfvars`, `*.tfstate` and `.terraform/` are git-ignored, and `terraform.tfvars.example` holds only non-secret settings.
- AWS credentials come from `aws configure` on the laptop. GHCR uses the workflow's built-in `GITHUB_TOKEN`.
- Both containers run as non-root users.
- See [docs/trivy.md](docs/trivy.md) for what Trivy scans and how to read the result.

## Screenshots

All evidence screenshots are in [docs/screenshots/](docs/screenshots/).
