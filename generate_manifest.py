#!/usr/bin/env python3
"""
This script dynamically generates a single, unified Kubernetes manifest 
for deploying an API across 10 GKE regions using GKE Multi-cluster Gateway 
and Multi-cluster Services (MCS). This avoids configuration drift and 
manual manifest duplication (DRY principle).
"""

import json

# Define the 10 target GKE regions for global deployment
REGIONS = [
    "us-central1",      # Iowa, USA
    "us-east1",         # South Carolina, USA
    "europe-west1",     # Belgium
    "europe-west3",     # Frankfurt, Germany
    "asia-east1",       # Taiwan
    "asia-northeast1",  # Tokyo, Japan
    "australia-southeast1", # Sydney, Australia
    "southamerica-east1",   # Sao Paulo, Brazil
    "us-west1",         # Oregon, USA
    "europe-north1"     # Finland
]

APP_NAME = "global-api"
IMAGE_VERSION = "v2.1.0"
PORT = 8080

def generate_gke_gateway():
    """
    Generates the Global Multi-cluster Gateway and HTTPRoute.
    This single gateway routes global traffic to the nearest healthy region.
    """
    gateway_yaml = f"""---
apiVersion: gateway.networking.k8s.io/v1beta1
kind: Gateway
metadata:
  name: global-api-gateway
  namespace: multi-cluster-gateways
  annotations:
    networking.gke.io/cert-key: "global-api-cert"
spec:
  gatewayClassName: gke-l7-global-external-managed-mc
  listeners:
  - name: http
    port: 80
    protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  name: global-api-route
  namespace: multi-cluster-gateways
spec:
  parentRefs:
  - name: global-api-gateway
    namespace: multi-cluster-gateways
  rules:
  - backendRefs:
    # Route traffic to the MultiClusterService
    - group: net.gke.io
      kind: MultiClusterService
      name: {APP_NAME}-mcs
      port: {PORT}
"""
    return gateway_yaml

def generate_regional_resources(region):
    """
    Generates regional Deployment, Service, and ServiceExport resources.
    Using ServiceExport registers the regional service into the MultiClusterService.
    """
    resources = f"""---
# Regional Deployment for {region}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {APP_NAME}-{region}
  namespace: default
  labels:
    app: {APP_NAME}
    region: {region}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {APP_NAME}
      region: {region}
  template:
    metadata:
      labels:
        app: {APP_NAME}
        region: {region}
    spec:
      containers:
      - name: api-server
        image: gcr.io/my-global-project/{APP_NAME}:{IMAGE_VERSION}
        ports:
        - containerPort: {PORT}
        env:
        - name: REGION
          value: "{region}"
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "200m"
            memory: "256Mi"
---
# Regional Service for {region}
apiVersion: v1
kind: Service
metadata:
  name: {APP_NAME}-{region}
  namespace: default
  labels:
    app: {APP_NAME}
    region: {region}
spec:
  selector:
    app: {APP_NAME}
    region: {region}
  ports:
  - protocol: TCP
    port: {PORT}
    targetPort: {PORT}
---
# Export regional service to the global MultiClusterService mesh
apiVersion: net.gke.io/v1
kind: ServiceExport
metadata:
  name: {APP_NAME}-{region}
  namespace: default
"""
    return resources

def main():
    print("# ======================================================================")
    print(f"# DYNAMICALLY GENERATED MULTI-REGION MANIFEST FOR: {APP_NAME.upper()}")
    print(f"# Target Regions Count: {len(REGIONS)}")
    print("# Generated via DRY Automation Script to prevent Configuration Drift.")
    print("# ======================================================================\n")
    
    # 1. Generate Global Gateway Routing
    print(generate_gke_gateway())
    
    # 2. Generate Resources for all 10 regions
    for region in REGIONS:
        print(generate_regional_resources(region))

if __name__ == "__main__":
    main()
