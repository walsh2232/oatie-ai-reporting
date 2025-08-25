# Production environment Terraform configuration
terraform {
  required_version = ">= 1.5"
  
  backend "s3" {
    bucket         = "oatie-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "oatie-terraform-locks"
  }
  
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

# Provider configuration
provider "kubernetes" {
  config_path = var.kubeconfig_path
  config_context = var.kubeconfig_context
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
    config_context = var.kubeconfig_context
  }
}

# Local values
locals {
  environment = "production"
  namespace   = "oatie-ai-production"
  
  common_labels = {
    environment = local.environment
    project     = "oatie-ai"
    managed_by  = "terraform"
  }
}

# Kubernetes infrastructure module
module "kubernetes" {
  source = "../../modules/kubernetes"
  
  namespace   = local.namespace
  environment = local.environment
  
  # Application configuration
  debug     = false
  log_level = "INFO"
  
  # Database and cache
  database_url = var.database_url
  redis_url    = var.redis_url
  
  # Security
  secret_key     = var.secret_key
  encryption_key = var.encryption_key
  cors_origins   = var.cors_origins
  allowed_hosts  = var.allowed_hosts
  
  # Performance
  async_workers        = 8
  connection_pool_size = 100
  query_timeout       = 30
  
  # Monitoring
  monitoring_enabled = true
  
  # External services
  oracle_bi_url      = var.oracle_bi_url
  oracle_bi_username = var.oracle_bi_username
  oracle_bi_timeout  = 30
  
  # Security policies
  network_policy_enabled = true
  resource_quota_enabled = true
  
  # Resource quotas
  quota_requests_cpu    = "16"
  quota_requests_memory = "32Gi"
  quota_limits_cpu      = "32"
  quota_limits_memory   = "64Gi"
  quota_pod_count       = 100
  quota_service_count   = 30
}

# Monitoring module
module "monitoring" {
  source = "../../modules/monitoring"
  
  namespace   = module.kubernetes.namespace_name
  environment = local.environment
  
  # Prometheus configuration
  prometheus_enabled           = true
  prometheus_retention_days    = 30
  prometheus_storage_size      = "50Gi"
  prometheus_storage_class     = "fast-ssd"
  
  # Grafana configuration
  grafana_enabled              = true
  grafana_admin_password       = var.grafana_admin_password
  grafana_storage_size         = "10Gi"
  
  # Alerting
  alertmanager_enabled         = true
  slack_webhook_url           = var.slack_webhook_url
  pagerduty_integration_key   = var.pagerduty_integration_key
  
  depends_on = [module.kubernetes]
}

# Deploy Oatie application using Helm
resource "helm_release" "oatie" {
  name       = "oatie"
  repository = "../../helm"
  chart      = "oatie"
  namespace  = module.kubernetes.namespace_name
  version    = var.chart_version
  
  # Production values
  values = [
    yamlencode({
      environment = local.environment
      
      image = {
        backend = {
          repository = var.backend_image_repository
          tag        = var.backend_image_tag
          pullPolicy = "Always"
        }
        frontend = {
          repository = var.frontend_image_repository
          tag        = var.frontend_image_tag
          pullPolicy = "Always"
        }
      }
      
      # Deployment strategy
      deploymentStrategy = {
        type = "blue-green"
        blueGreen = {
          productionSlot         = var.production_slot
          previewSlot           = var.preview_slot
          autoPromotionEnabled  = false
          scaleDownDelaySeconds = 30
        }
      }
      
      # Backend configuration
      backend = {
        replicaCount = var.backend_replica_count
        
        autoscaling = {
          enabled                        = true
          minReplicas                   = var.backend_min_replicas
          maxReplicas                   = var.backend_max_replicas
          targetCPUUtilizationPercentage = 70
          targetMemoryUtilizationPercentage = 80
        }
        
        resources = {
          requests = {
            cpu    = "1000m"
            memory = "1Gi"
          }
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }
        
        service = {
          type = "ClusterIP"
        }
      }
      
      # Frontend configuration
      frontend = {
        replicaCount = var.frontend_replica_count
        
        autoscaling = {
          enabled                        = true
          minReplicas                   = var.frontend_min_replicas
          maxReplicas                   = var.frontend_max_replicas
          targetCPUUtilizationPercentage = 70
        }
        
        resources = {
          requests = {
            cpu    = "500m"
            memory = "512Mi"
          }
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        
        service = {
          type = "LoadBalancer"
        }
      }
      
      # Ingress configuration
      ingress = {
        enabled   = true
        className = "nginx"
        hosts = [
          {
            host = var.frontend_domain
            paths = [
              {
                path     = "/"
                pathType = "Prefix"
                service  = "frontend"
              }
            ]
          },
          {
            host = var.backend_domain
            paths = [
              {
                path     = "/"
                pathType = "Prefix"
                service  = "backend"
              }
            ]
          }
        ]
        tls = [
          {
            secretName = "oatie-tls-cert"
            hosts      = [var.frontend_domain, var.backend_domain]
          }
        ]
      }
      
      # Database (external)
      postgresql = {
        enabled = false
      }
      
      # Redis (external)
      redis = {
        enabled = false
      }
      
      # Configuration
      config = {
        app = {
          debug      = false
          logLevel   = "INFO"
          secretKey  = var.secret_key
          encryptionKey = var.encryption_key
        }
        
        security = {
          corsOrigins    = var.cors_origins
          allowedHosts   = var.allowed_hosts
          rateLimitRequests = 1000
          rateLimitWindow   = 3600
        }
        
        performance = {
          asyncWorkers        = 8
          connectionPoolSize  = 100
          queryTimeout       = 30
          maxQueryComplexity = 1000
        }
        
        monitoring = {
          enabled         = true
          metricsEndpoint = "/metrics"
        }
        
        external = {
          oracleBiUrl      = var.oracle_bi_url
          oracleBiUsername = var.oracle_bi_username
          oracleBiPassword = var.oracle_bi_password
        }
      }
      
      # Secrets
      secrets = {
        values = {
          databaseUrl   = var.database_url
          redisUrl      = var.redis_url
          secretKey     = var.secret_key
          encryptionKey = var.encryption_key
        }
      }
      
      # Monitoring
      monitoring = {
        prometheus = {
          enabled = true
          serviceMonitor = {
            enabled = true
          }
        }
        
        grafana = {
          enabled = true
          dashboards = {
            enabled = true
          }
        }
        
        alerts = {
          enabled = true
        }
      }
      
      # Security
      networkPolicy = {
        enabled = true
      }
      
      podDisruptionBudget = {
        enabled = true
        minAvailable = 2
      }
    })
  ]
  
  depends_on = [module.kubernetes, module.monitoring]
}