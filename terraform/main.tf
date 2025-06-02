# Configuración de Terraform y providers
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configuración del provider AWS
provider "aws" {
  region = var.aws_region
}

# DynamoDB para almacenar configuraciones del bot
resource "aws_dynamodb_table" "bot_config" {
  name           = "${var.project_name}-config"
  billing_mode   = "PAY_PER_REQUEST"  # Solo pagas por lo que uses
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"  # String
  }

  tags = {
    Name = "${var.project_name}-config"
  }
}

# Rol IAM para que Lambda pueda ejecutarse
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Políticas de permisos para Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.bot_config.arn
      }
    ]
  })
}

# Función Lambda (el cerebro del bot)
# En tu main.tf, actualiza la sección environment del Lambda:

resource "aws_lambda_function" "chatbot" {
  filename         = "chatbot.zip"
  function_name    = "${var.project_name}-handler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      DYNAMODB_TABLE       = aws_dynamodb_table.bot_config.name
      BOT_TOKEN           = var.bot_token
      DISCORD_APP_ID      = var.discord_app_id
      DISCORD_PUBLIC_KEY  = var.discord_public_key
    }
  }
}

# API Gateway - punto de entrada HTTP
resource "aws_api_gateway_rest_api" "chatbot_api" {
  name        = "${var.project_name}-api"
  description = "API Gateway for Discord/Slack bot"
}

# Recurso /webhook en la API
resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.chatbot_api.id
  parent_id   = aws_api_gateway_rest_api.chatbot_api.root_resource_id
  path_part   = "webhook"
}

# Método POST para el webhook
resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.chatbot_api.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integración entre API Gateway y Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.chatbot_api.id
  resource_id = aws_api_gateway_resource.webhook.id
  http_method = aws_api_gateway_method.webhook_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.chatbot.invoke_arn
}

# Despliegue de la API
resource "aws_api_gateway_deployment" "chatbot_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]

  rest_api_id = aws_api_gateway_rest_api.chatbot_api.id
  stage_name  = "prod"
}

# Permiso para que API Gateway invoque Lambda
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chatbot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.chatbot_api.execution_arn}/*/*"
}