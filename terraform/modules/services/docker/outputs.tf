# output "lambda_name" {
#   value = var.lambda_image_name
# }

output "lambda_arn" {
  value = aws_lambda_function.lambda_function_from_image.*.arn
}

output "function_name" {
  value = aws_lambda_function.lambda_function_from_image.function_name
}

output "image_uri" {
  value = aws_lambda_function.lambda_function_from_image.lambda_image_uri
}

output "image_tag" {
  value = docker_image.lambda_image.build.tag
}