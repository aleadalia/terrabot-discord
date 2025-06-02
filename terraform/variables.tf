variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "terrabot-discord"
}

variable "bot_token" {
  description = "Discord bot token"
  type        = string
  sensitive   = true
}

variable "discord_app_id" {
  description = "Discord Application ID"
  type        = string
  default     = ""
}

variable "discord_public_key" {
  description = "Discord Public Key"
  type        = string
  default     = ""
  sensitive   = true
}