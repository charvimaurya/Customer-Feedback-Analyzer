variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "app_name" {
  description = "The name of the application"
  type        = string
  default     = "customer-feedback-analyzer"
}

variable "db_password" {
  description = "Password for the database user"
  type        = string
  sensitive   = true
}
