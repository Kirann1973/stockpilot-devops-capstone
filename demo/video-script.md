# Video script (about 10 minutes)

## Before you press record

Have these ready:

- **Terminal tab "tunnel":** `minikube tunnel` is running.
- **Terminal tab "argocd":** `kubectl port-forward -n argocd svc/argocd-server 8081:443` is running.
- **Terminal tab "prom":** `kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090` is running.
- **Terminal tab "grafana":** `kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80` is running.
- **Terminal tab "work":** `cd ~/stockpilot-devops-capstone && git pull`.
- **Safari tabs, in this order:**
  1. the repo
  2. its Actions page
  3. https://localhost:8081 (Argo CD, logged in)
  4. http://stockpilot.local
  5. http://localhost:9090/targets
  6. http://localhost:3001 (Grafana, StockPilot API dashboard)
- **The slide PDF:** `demo/StockPilot-presentation.pdf`, open in Preview.

## 1. Slides (about 3 min)

Open the PDF in Preview and go full screen with View → Slideshow. Say one or two sentences per slide.

1. "Hi, I'm Kiran, roll number 10446. My capstone is StockPilot, an inventory management app that I took all the way through a DevOps pipeline."
2. **Overview.** "It tracks products, stock levels and reorder points, and flags low or out-of-stock items."
3. **Tech stack.** "React and FastAPI with PostgreSQL. Docker, GitHub Actions, Trivy, Terraform on AWS, Kubernetes with Helm and Argo CD, and Prometheus with Grafana."
4. **Architecture.** "A push goes through GitHub Actions to GHCR. Argo CD syncs the Helm chart into the cluster, the Ingress routes `/` to the frontend and `/api` to the backend, and Prometheus scrapes the backend."
5. **CI/CD.** "Tests run first. Then images are built, scanned by Trivy, and pushed tagged with the commit SHA. Finally the new tag is committed for Argo CD."
6. **Trivy.** "My first run was blocked by 7 HIGH CVEs. I upgraded FastAPI and removed pip and setuptools from the image, and the later runs were clean."
7. **Terraform.** "A VPC with 2 public and 2 private subnets plus EKS with 2 nodes in Mumbai. I created all 58 resources, verified them, and destroyed them."
8. **Kubernetes.** "Two replicas each, an Ingress, and an HPA that scaled the backend from 2 to 6 pods under load."
9. **Observability.** "Prometheus scrapes every backend pod, and Grafana shows requests per second, latency and pods."
10. **Learnings.** Read the six card titles.
11. "Now the live walkthrough." Press Esc.

## 2. Trigger a push (about 1 min, then let it run)

In the "work" tab:

```bash
open -e frontend/src/App.jsx
```

Find `Track stock levels, spot shortages and restock on time.` and change it, for example to `Live demo for Kiran, roll 10446: stock tracking on Kubernetes.` Save with Cmd + S. Then run:

```bash
git commit -am "Update dashboard subtitle for the live demo"
git push
```

Open the Actions tab in Safari and say: "The push started the pipeline. While it runs, here's the code."

## 3. Codebase (about 1 min)

In the repo tab, click through the folders and say what each one is:

- `backend/app`: routes, models and schemas
- `backend/tests`: 14 pytest tests
- `frontend/src`
- `.github/workflows/ci-cd.yml`
- `terraform`
- `helm/stockpilot/templates`
- `argocd`
- `monitoring`

## 4. Terraform (about 1 min)

1. Open `terraform/main.tf` and say: "VPC module and EKS module."
2. Open `docs/screenshots` and click through these, saying one line each:
   - `08-terraform-plan.png`: "plan: 58 to add"
   - `09a-aws-vpc.png` and `09b-aws-subnets.png`
   - `09c-aws-eks.png` and `09d-aws-nodegroup.png`
   - `09e-eks-nodes.png`: "two nodes Ready"
   - `10-terraform-destroy.png`: "58 destroyed"

## 5. Kubernetes (about 1 min)

In the "work" tab:

```bash
kubectl get pods,svc,ingress,hpa -n stockpilot
helm list -n stockpilot
```

Say: "Two frontend and two backend pods, Postgres, ClusterIP services, the Ingress, and the HPA." Then open http://stockpilot.local.

## 6. Prometheus and Grafana (about 1 min)

1. Open the Prometheus tab and type `stockpilot` in the filter. Say: "Every backend pod is UP."
2. Open the Grafana tab and say: "Live requests per second, p95 latency, pods and CPU."

## 7. Pipeline result + Argo CD (about 2 min)

1. Open the Actions tab. The run should be green by now: Test, Terraform, Build/Trivy/push, GitOps bump. Open the Trivy step and say: "0 HIGH or CRITICAL."
2. Open the Argo CD tab, open the **stockpilot** app, and click **Refresh**. Say: "Argo CD saw the new image tag in Git and is syncing." Wait until it shows **Synced / Healthy**.
3. Open http://stockpilot.local and refresh the page. Say: "The new subtitle is live. It went from git push to Kubernetes with no manual deploy."
4. End with: "Thank you."

Then stop the recording.
