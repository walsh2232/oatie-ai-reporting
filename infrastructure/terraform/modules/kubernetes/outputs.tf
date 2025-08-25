# Output values from the Kubernetes module

output "namespace_name" {
  description = "Name of the created Kubernetes namespace"
  value       = kubernetes_namespace.oatie.metadata[0].name
}

output "backend_service_account_name" {
  description = "Name of the backend service account"
  value       = kubernetes_service_account.oatie_backend.metadata[0].name
}

output "frontend_service_account_name" {
  description = "Name of the frontend service account"
  value       = kubernetes_service_account.oatie_frontend.metadata[0].name
}

output "secrets_name" {
  description = "Name of the application secrets"
  value       = kubernetes_secret.oatie_secrets.metadata[0].name
}

output "config_map_name" {
  description = "Name of the backend configuration ConfigMap"
  value       = kubernetes_config_map.oatie_backend_config.metadata[0].name
}

output "network_policy_name" {
  description = "Name of the network policy (if enabled)"
  value       = var.network_policy_enabled ? kubernetes_network_policy.oatie_network_policy[0].metadata[0].name : null
}

output "resource_quota_name" {
  description = "Name of the resource quota (if enabled)"
  value       = var.resource_quota_enabled ? kubernetes_resource_quota.oatie_quota[0].metadata[0].name : null
}

output "backend_pdb_name" {
  description = "Name of the backend pod disruption budget"
  value       = kubernetes_pod_disruption_budget_v1.backend_pdb.metadata[0].name
}

output "frontend_pdb_name" {
  description = "Name of the frontend pod disruption budget"
  value       = kubernetes_pod_disruption_budget_v1.frontend_pdb.metadata[0].name
}