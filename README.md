# GKE Multi Region API Deployment Generator

This Python script dynamically generates a single, unified Kubernetes manifest for deploying an API across 10 GKE regions. It utilizes GKE Multi-cluster Gateway API resources (Gateway, HTTPRoute, ServiceExport) to demonstrate DRY (Don't Repeat Yourself) configuration management without manual duplication.

## Language

`python`

## How to Run

Run 'python generate_manifest.py' to output the complete multi-region YAML manifest. You can pipe the output directly to a file: 'python generate_manifest.py > multi-region-deploy.yaml'

## Original Article

This example accompanies the Turkish article: [GKE ile 10 Bölgede Tek Manifest ile API Dağıtımı](https://fatihsoysal.com/blog/gke-ile-10-bolgede-tek-manifest-ile-api-dagitimi/).

## License

MIT — see [LICENSE](LICENSE).
