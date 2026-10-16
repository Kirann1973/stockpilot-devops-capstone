# Monitoring: Prometheus + Grafana

1. Install kube-prometheus-stack with `kube-prometheus-stack-values.yaml` (command at the top of the file).
2. Deploy (or re-deploy) StockPilot with Helm **after** the stack, so the `ServiceMonitor` CRD exists.
3. Prometheus targets: `kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090` → http://localhost:9090/targets, look for `serviceMonitor/stockpilot/stockpilot-backend` = UP.
4. Grafana: `kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80` → http://localhost:3001 (admin / stockpilot-admin). Dashboard **StockPilot API** is provisioned automatically from the Helm chart.
5. Generate traffic so the panels move: `./scripts/load-test.sh`.
