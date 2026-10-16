# Argo CD (GitOps)

Argo CD watches this repository and keeps the cluster equal to what is on `main`.

```text
git push ──► GitHub Actions: test → build → Trivy → push image :<sha>
                     └─► "GitOps: bump image tag" job commits the new <sha>
                         into helm/stockpilot/values-gitops.yaml
                                   │
Argo CD polls main (or click Refresh) ──► sees the new tag ──► syncs the Helm chart
                                   │
                    Deployments roll to the new image, no kubectl/helm by hand
```

## Install on Minikube

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait -n argocd --for=condition=available deploy --all --timeout=600s

kubectl apply -f argocd/stockpilot-app.yaml
```

## Open the UI

```bash
# admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
kubectl port-forward -n argocd svc/argocd-server 8081:443
```

Open https://localhost:8081 (accept the self-signed certificate), log in as `admin`.
The **stockpilot** app should show **Synced** and **Healthy**.

## Notes

- Argo CD adopts the resources the earlier `helm upgrade --install` created, because both use release name `stockpilot`.
- `ignoreDifferences` on `/spec/replicas` lets the HPA scale the backend without Argo CD fighting it.
- Argo CD checks Git every 3 minutes. Click **Refresh** in the UI to sync right away.
