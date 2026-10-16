# Terraform: AWS VPC + EKS for StockPilot

Creates in `ap-south-1` (Mumbai) by default:

```
VPC 10.30.0.0/16
 ├── 2 public subnets  (load balancers, NAT gateway)
 ├── 2 private subnets (EKS worker nodes)
 ├── Internet gateway + 1 NAT gateway
 └── EKS cluster "stockpilot-eks"
       └── managed node group "main" (2 × t3.medium)
```

## Usage

```bash
aws configure                      # access key, secret, region ap-south-1
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check && terraform validate
terraform plan -out tfplan
terraform apply tfplan             # ~15-20 minutes
aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks
kubectl get nodes
```

## Tear down (do this the same day)

```bash
terraform destroy                  # ~10-15 minutes
```

Approximate cost while running: EKS control plane $0.10/h + 2 × t3.medium + NAT gateway, roughly **$0.25–0.30 per hour**.

No credentials are stored in this folder. `terraform.tfvars`, `*.tfstate` and `.terraform/` are git-ignored.
