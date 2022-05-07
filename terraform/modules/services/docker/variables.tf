# TAGS
variable "tags" {
  type = map
  description = "Tags for lambda"
  default = {}
}

# LABELS
variable "labels" {
  type = map
  description = "Labels for lambda image"
  default = {}
}

# LABELS
variable "build_args" {
  type = map(any)
  description = "Build args for lambda image"
  default = {}
}

# ENV VARS
variable "environment_variables" {
  type = map
  description = "Environment variables"
}

#SETUP
variable "region" {
  description = "Region of Lambda & S3 source code"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
}

variable "lambda_description" {
  description = "Lambda description"
}

variable "create_package" {
  description = "Creates package with lambda function. Research more idk."
  default = false
}

variable "ecr_repo" {
  description = "link to ECR-repo"
}

variable "source_path" {
}

variable "lambda_image_tag" {
  description = "Image tag for newly created Dockerfile image"
}

variable "lambda_image_uri" {
  type = string
  description = "Lambda image URI"
}


variable ecr_repo_lifecycle_policy {
  type        = map(any)
  description = "How should the lifecycle of images in ECR be handled"
}


variable create_ecr_repo {
  type = bool
  description = "Creates an ECR repo for the image to be uploaded to. This is so the lambda can access the image."
  default = true
}

variable "lambda_role" {
  description = "IAM role attached to Lambda function - ARN"
}

variable "lambda_timeout" {
  description = "Maximum runtime for Lambda"
  default = 30
}

variable "lambda_image_name" {
  description = "Path to lambda code Dockerfile"
}

variable "lambda_memory_size" {
  description = "Lambda memory size"
  default = 128
}

variable "lambda_vpc_security_group_ids" {
  description = "Lambda VPC Security Group IDs"
  type = list(string)
  default = []
}

variable "lambda_vpc_subnet_ids" {
  description = "Lambda VPC Subnet IDs"
  type = list(string)
  default = []
}

variable "lambda_layers" {
  description = "Lambda Layer ARNS"
  type = list(string)
  default = []
}

variable "path_to_dockerfile" {
  type        = string
  description = "source path for Dockerfile to be built from"
}

