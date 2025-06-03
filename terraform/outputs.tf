output "api_gateway_url" {
  description = "API Gateway URL for webhook"
  value       = "https://${aws_api_gateway_rest_api.chatbot_api.id}.execute-api.${var.aws_region}.amazonaws.com/prod/webhook"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.chatbot.function_name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.bot_config.name
}

output "api_gateway_id" {
  description = "API Gateway ID"
  value       = aws_api_gateway_rest_api.chatbot_api.id
}