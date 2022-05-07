# output "lambda_name" {
#   value = var.lambda_image_name
# }

output "lambda_arn" {
  value = aws_lambda_function.lambda_function_from_image.*.arn
}

output "function_name" {
  value = aws_lambda_function.lambda_function_from_image.function_name
}
