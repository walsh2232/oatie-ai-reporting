# Terraform configuration for Kubernetes infrastructure
terraform {
  required_version = ">= 1.5"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# Kubernetes namespace
resource "kubernetes_namespace" "oatie" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name"     = "oatie"
      "app.kubernetes.io/instance" = var.environment
      "environment"                = var.environment
      "managed-by"                 = "terraform"
    }
    annotations = {
      "description" = "Oatie AI Oracle BI Publisher Platform - ${var.environment}"
    }
  }
}

# Service account for the application
resource "kubernetes_service_account" "oatie_backend" {
  metadata {
    name      = "oatie-backend"
    namespace = kubernetes_namespace.oatie.metadata[0].name
    labels = {
      "app.kubernetes.io/name"      = "oatie-backend"
      "app.kubernetes.io/component" = "backend"
      "app.kubernetes.io/instance"  = var.environment
    }
  }
  
  automount_service_account_token = true
}

# Service account for frontend
resource "kubernetes_service_account" "oatie_frontend" {
  metadata {
    name      = "oatie-frontend"
    namespace = kubernetes_namespace.oatie.metadata[0].name
    labels = {
      "app.kubernetes.io/name"      = "oatie-frontend"
      "app.kubernetes.io/component" = "frontend"
      "app.kubernetes.io/instance"  = var.environment
    }
  }
  
  automount_service_account_token = false
}

# Generate random secrets if not provided
resource "random_password" "secret_key" {
  count   = var.secret_key == "" ? 1 : 0
  length  = 64
  special = true
}

resource "random_password" "encryption_key" {
  count   = var.encryption_key == "" ? 1 : 0
  length  = 32
  special = false
}

# Application secrets
resource "kubernetes_secret" "oatie_secrets" {
  metadata {
    name      = "${var.namespace}-secrets"
    namespace = kubernetes_namespace.oatie.metadata[0].name
    labels = {
      "app.kubernetes.io/name"     = "oatie"
      "app.kubernetes.io/instance" = var.environment
    }
  }

  data = {
    database-url    = var.database_url
    redis-url       = var.redis_url
    secret-key      = var.secret_key != "" ? var.secret_key : random_password.secret_key[0].result
    encryption-key  = var.encryption_key != "" ? var.encryption_key : random_password.encryption_key[0].result
  }

  type = "Opaque"
}

# Application configuration
resource "kubernetes_config_map" "oatie_backend_config" {
  metadata {
    name      = "oatie-backend-config"
    namespace = kubernetes_namespace.oatie.metadata[0].name
    labels = {
      "app.kubernetes.io/name"      = "oatie-backend"
      "app.kubernetes.io/component" = "backend"
      "app.kubernetes.io/instance"  = var.environment
    }
  }

  data = {
    "app.yaml" = yamlencode({
      environment = var.environment
      debug       = var.debug
      log_level   = var.log_level
      
      # Security settings
      security = {
        cors_origins     = var.cors_origins
        allowed_hosts    = var.allowed_hosts
        rate_limit_requests = var.rate_limit_requests
        rate_limit_window   = var.rate_limit_window
      }
      
      # Performance settings
      performance = {
        async_workers         = var.async_workers
        connection_pool_size  = var.connection_pool_size
        query_timeout        = var.query_timeout
        max_query_complexity = var.max_query_complexity
      }
      
      # Monitoring settings
      monitoring = {
        enabled          = var.monitoring_enabled
        metrics_endpoint = var.metrics_endpoint
      }
      
      # External services
      external = {
        oracle_bi_url      = var.oracle_bi_url
        oracle_bi_username = var.oracle_bi_username
        oracle_bi_timeout  = var.oracle_bi_timeout
      }
    })
  }
}

# Network policy for security
resource "kubernetes_network_policy" "oatie_network_policy" {
  count = var.network_policy_enabled ? 1 : 0
  
  metadata {
    name      = "oatie-network-policy"
    namespace = kubernetes_namespace.oatie.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = {
        "app.kubernetes.io/name"     = "oatie"
        "app.kubernetes.io/instance" = var.environment
      }
    }

    policy_types = ["Ingress", "Egress"]

    # Ingress rules
    ingress {
      # Allow ingress from nginx ingress controller
      from {
        namespace_selector {
          match_labels = {
            name = "ingress-nginx"
          }
        }
      }
      
      # Allow ingress from monitoring namespace
      from {
        namespace_selector {
          match_labels = {
            name = "monitoring"
          }
        }
      }
      
      # Allow internal communication within namespace
      from {
        namespace_selector {
          match_labels = {
            name = kubernetes_namespace.oatie.metadata[0].name
          }
        }
      }
    }

    # Egress rules
    egress {
      # Allow DNS resolution
      to {}
      ports {
        port     = "53"
        protocol = "UDP"
      }
      ports {
        port     = "53"
        protocol = "TCP"
      }
    }
    
    egress {
      # Allow HTTPS traffic
      to {}
      ports {
        port     = "443"
        protocol = "TCP"
      }
    }
    
    egress {
      # Allow database connections
      to {}
      ports {
        port     = "5432"
        protocol = "TCP"
      }
    }
    
    egress {
      # Allow Redis connections
      to {}
      ports {
        port     = "6379"
        protocol = "TCP"
      }
    }
  }
}

# Pod disruption budget for backend
resource "kubernetes_pod_disruption_budget_v1" "backend_pdb" {
  metadata {
    name      = "oatie-backend-pdb"
    namespace = kubernetes_namespace.oatie.metadata[0].name
  }
  
  spec {
    min_available = 1
    selector {
      match_labels = {
        "app.kubernetes.io/name"      = "oatie-backend"
        "app.kubernetes.io/instance"  = var.environment
      }
    }
  }
}

# Pod disruption budget for frontend
resource "kubernetes_pod_disruption_budget_v1" "frontend_pdb" {
  metadata {
    name      = "oatie-frontend-pdb"
    namespace = kubernetes_namespace.oatie.metadata[0].name
  }
  
  spec {
    min_available = 1
    selector {
      match_labels = {
        "app.kubernetes.io/name"      = "oatie-frontend"
        "app.kubernetes.io/instance"  = var.environment
      }
    }
  }
}

# Resource quota
resource "kubernetes_resource_quota" "oatie_quota" {
  count = var.resource_quota_enabled ? 1 : 0
  
  metadata {
    name      = "oatie-resource-quota"
    namespace = kubernetes_namespace.oatie.metadata[0].name
  }
  
  spec {
    hard = {
      "requests.cpu"    = var.quota_requests_cpu
      "requests.memory" = var.quota_requests_memory
      "limits.cpu"      = var.quota_limits_cpu
      "limits.memory"   = var.quota_limits_memory
      "persistentvolumeclaims" = var.quota_pvc_count
      "pods"            = var.quota_pod_count
      "services"        = var.quota_service_count
    }
  }
}