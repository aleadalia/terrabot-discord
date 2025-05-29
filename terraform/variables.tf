variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "simple-chatbot"
}

variable "bot_token" {
  description = "Discord/Slack bot token"
  type        = string
  sensitive   = true
}