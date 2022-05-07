#TAGS
variable "tags" {
  type        = map(any)
  description = "Tags for lambda"
  default     = {}
}


#Environment variables
variable "environment_variables" {
  type        = map(any)
  description = "Environment variables"
}


#SETUP

#Global
variable "region" {
  type        = string
  description = "The region in which to create/manage resources"
  default     = "us-east-2"
}

variable "project" {
  type        = string
  description = "Name of project"
}

#Lambda
variable "lambda_function_name" {
  type        = string
  description = "Local path to Lambda zip code"
}

variable "lambda_description" {
  default     = ""
  description = "Lambda description"
}


variable "lambda_timeout" {
  description = "Maximum runtime for Lambda"
  default     = 30
}

variable "lambda_image_name" {
  default     = "../app/Dockerfile"
  description = "Path to lambda code Dockerfile"
}

variable "lambda_image_uri" {
  description = "URI for Docker image"
}


variable "lambda_memory_size" {
  description = "Lambda memory size"
}

variable "lambda_vpc_security_group_ids" {
  description = "Lambda VPC Security Group IDs"
  type        = list(string)
  default     = []
}

variable "lambda_vpc_subnet_ids" {
  description = "Lambda VPC Subnet IDs"
  type        = list(string)
  default     = []
}

variable "lambda_layers" {
  type        = list(string)
  description = "Lambda Layer ARNS"
  default     = []
}

#API Gateway Setup
variable "api_gw_method" {
  type        = string
  description = "API Gateway method (GET,POST...)"
  default     = "POST"
}

variable "api_gw_dependency_list" {
  type        = list(any)
  description = "List of aws_api_gateway_integration* that require aws_api_gateway_deployment dependency"
  default     = []
}

variable "api_gw_disable_resource_creation" {
  type        = bool
  description = "Specify whether to create or not the default /api/messages path or stop at /api"
  default     = "false"
}

variable "api_gw_endpoint_configuration_type" {
  type        = string
  description = "Specify the type of endpoint for API GW to be setup as. [EDGE, REGIONAL, PRIVATE]. Defaults to EDGE"
  default     = "EDGE"
}

#DynamoDB
variable "dynamodb_table_properties" {
  type        = list(any)
  description = "List of maps representing a table each. name (required), read_capacity(default=1), write_capacity(default=1), hash_key(required)"
}

variable "dynamodb_table_attributes" {
  type        = list(any)
  description = "List of list of maps representing each table attributes list. Required due to current HCL limitations"
}

variable "dynamodb_table_secondary_index" {
  type        = list(any)
  default     = [[]]
  description = "List of list of maps representing each table secondary index list. Required due to current HCL limitations"
}

variable "dynamodb_table_local_secondary_index" {
  type        = list(any)
  default     = [[]]
  description = "List of list of maps representing each table local secondary index list. Required due to current HCL limitations"
}

variable "dynamodb_policy_action_list" {
  description = "List of Actions to be executed"
  type        = list(any)
  default     = ["dynamodb:DescribeTable", "dynamodb:DeleteItem", "dynamodb:GetItem", "dynamodb:Scan", "dynamodb:Query"]
}

variable "dynamodb_table_ttl" {
  type        = list(any)
  default     = [[]]
  description = "List of list of maps representing each table local secondary index list. Required due to current HCL limitations"
}

# Docker

