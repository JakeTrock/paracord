resource "random_pet" "this" {
  length = 2
}

resource "aws_lambda_function" "lambda_function_from_image" {

  function_name = var.function_name
  image_name    = resource.docker_image.name
  description   = var.description

  create_package = var.create_package

  ##################
  # Container Image
  ##################
  image_uri    = module.docker.image_uri
  package_type = "Image"

  # count            = var.lambda_image_name == "" ? 0 : 1
  role        = var.lambda_role # data.template_file.lambda_dynamodb_policy.rendered
  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size
  # layers           = var.lambda_layers

  vpc_config {
    security_group_ids = var.lambda_vpc_security_group_ids
    subnet_ids         = var.lambda_vpc_subnet_ids
  }

  environment {
    variables = var.environment_variables
  }

  tags = var.tags

}


