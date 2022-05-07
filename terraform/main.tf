
#required otherwise circular dependency between IAM and Lambda
locals {
  lambda_function_name  = "${var.project}-${var.lambda_function_name}-${terraform.workspace}"
  dynamodb_tables_count = length(var.dynamodb_table_properties)
}

# provider "aws" {
#   region = "us-east-2"
# }

# resource "random_pet" "this" {
#   length = 2
# }

module "apigw" {
  source = "./modules/services/api-gateway"

  #Setup
  api_gw_name                        = "${var.project}-API-Gateway-${terraform.workspace}"
  api_gw_disable_resource_creation   = var.api_gw_disable_resource_creation
  api_gw_endpoint_configuration_type = var.api_gw_endpoint_configuration_type
  stage_name                         = terraform.workspace
  method                             = var.api_gw_method
  lambda_arn                         = module.lambda.lambda_arn
  region                             = var.region
  lambda_name                        = module.lambda.function_name

  dependency_list = var.api_gw_dependency_list
}

module "lambda" {
  source = "./modules/services/lambda"
  # version = "v1.0.0"

  #Global
  region = "us-east-2"
  # project = "paracord"

  #Lambda
  function_name                 = var.lambda_function_name
  lambda_image_name             = module.ecr.name
  lambda_image_uri              = module.ecr.repository_url
  image_tag                     = "latest"
  description                   = var.lambda_description
  lambda_timeout                = var.lambda_timeout
  lambda_memory_size            = 256
  # lambda_dynamodb_policy        = module.iam.template_file.lambda_dynamodb_policy
  # lambda_vpc_security_group_ids = [aws_security_group.vpc_security_group.id]
  # lambda_vpc_subnet_ids         = [aws_subnet.vpc_subnet_a.id]
  # lambda_layers                 = [data.aws_lambda_layer_version.layer.arn]
  lambda_role                   = module.iam.lambda_role

  path_to_dockerfile = var.path_to_dockerfile
  ecr_repo           = var.ecr_repo
  create_ecr_repo    = var.create_ecr_repo
  source_path        = var.path_to_dockerfile
  build_args = {
    is_test = false # hook this up to docker image?
  }
  ecr_repo_lifecycle_policy = data.template_file.ecr_repo_lifecycle_policy.rendered

  #Tags
  tags = {
    project   = "Paracord"
    managedby = "Terraform"
  }

  #Lambda Environment variables
  environment_variables = {
    NODE_ENV = "development"
  }
  # depends_on = [
  #   module.iam.lambda_dynamodb_policy
  # ]
}


module "dynamodb" {
  source = "./modules/services/dynamodb"
  # version = "v1.0.0"

  #Global
  # region = var.region
  # project = var.project

  #Setup
  dynamodb_table_properties            = var.dynamodb_table_properties
  dynamodb_table_attributes            = var.dynamodb_table_attributes
  dynamodb_table_local_secondary_index = var.dynamodb_table_local_secondary_index
  dynamodb_table_secondary_index       = var.dynamodb_table_secondary_index
  dynamodb_table_ttl                   = var.dynamodb_table_ttl

  #Tags
  tags = var.tags

}

# IAM
module "iam" {
  source = "./modules/global/iam"

  #Setup
  lambda_name                 = local.lambda_function_name
  lambda_role                 = var.lambda_role_arn
  lambda_layers               = var.lambda_layers
  api_gw_name                 = module.apigw.api_gw_name
  api_gw_id                   = module.apigw.api_gw_id
  dynamodb_arn_list           = module.dynamodb.dynamodb_table_arns
  dynamodb_policy_action_list = var.dynamodb_policy_action_list
  dynamodb_tables_count       = local.dynamodb_tables_count
}

module "ecr" {
  source = "./modules/services/ecr"

  # Setup
  name = var.ecr_name
  image_tag_mutability = var.ecr_image_tag_mutability
  tags = var.ecr_tags
  policy = ver.ecr_policy
  lifecycle_policy = var.ecr_repo_lifecycle_policy
  encryption_type = var.ecr_encryption_type
  kms_key = var.ecr_kms_key
  scan_on_push = var.ecr_scan_on_push
  image_scanning_configuration = var.ecr_image_scanning_configuration
  timeouts = var.ecr_timeouts


}