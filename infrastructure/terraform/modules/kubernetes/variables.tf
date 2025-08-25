# Input variables for the Kubernetes module

variable "namespace" {
  description = "Kubernetes namespace for the application"
  type        = string
  default     = "oatie-ai"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

# Application configuration
variable "debug" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
  }
}

# Database configuration
variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection URL"
  type        = string
  sensitive   = true
}

# Security configuration
variable "secret_key" {
  description = "JWT secret key (leave empty to auto-generate)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "encryption_key" {
  description = "Data encryption key (leave empty to auto-generate)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "cors_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "allowed_hosts" {
  description = "Allowed hosts for the application"
  type        = list(string)
  default     = ["*"]
}

variable "rate_limit_requests" {
  description = "Rate limit requests per window"
  type        = number
  default     = 1000
}

variable "rate_limit_window" {
  description = "Rate limit window in seconds"
  type        = number
  default     = 3600
}

# Performance configuration
variable "async_workers" {
  description = "Number of async workers"
  type        = number
  default     = 4
}

variable "connection_pool_size" {
  description = "Database connection pool size"
  type        = number
  default     = 100
}

variable "query_timeout" {
  description = "Query timeout in seconds"
  type        = number
  default     = 30
}

variable "max_query_complexity" {
  description = "Maximum query complexity"
  type        = number
  default     = 1000
}

# Monitoring configuration
variable "monitoring_enabled" {
  description = "Enable monitoring"
  type        = bool
  default     = true
}

variable "metrics_endpoint" {
  description = "Metrics endpoint path"
  type        = string
  default     = "/metrics"
}

# External services
variable "oracle_bi_url" {
  description = "Oracle BI Publisher URL"
  type        = string
  default     = ""
}

variable "oracle_bi_username" {
  description = "Oracle BI Publisher username"
  type        = string
  default     = ""
  sensitive   = true
}

variable "oracle_bi_timeout" {
  description = "Oracle BI Publisher timeout in seconds"
  type        = number
  default     = 30
}

# Network policy
variable "network_policy_enabled" {
  description = "Enable network policies"
  type        = bool
  default     = true
}

# Resource quota
variable "resource_quota_enabled" {
  description = "Enable resource quota"
  type        = bool
  default     = false
}

variable "quota_requests_cpu" {
  description = "CPU requests quota"
  type        = string
  default     = "8"
}

variable "quota_requests_memory" {
  description = "Memory requests quota"
  type        = string
  default     = "16Gi"
}

variable "quota_limits_cpu" {
  description = "CPU limits quota"
  type        = string
  default     = "16"
}

variable "quota_limits_memory" {
  description = "Memory limits quota"
  type        = string
  default     = "32Gi"
}

variable "quota_pvc_count" {
  description = "Persistent volume claim count quota"
  type        = number
  default     = 10
}

variable "quota_pod_count" {
  description = "Pod count quota"
  type        = number
  default     = 50
}

variable "quota_service_count" {
  description = "Service count quota"
  type        = number
  default     = 20
}