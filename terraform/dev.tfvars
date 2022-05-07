# Global
project = "paracord"
region = "us-east-2"

# API_GW
api_gw_name                           = "paracord_rest_api"
api_gw_disable_resource_creation      = false
api_gw_endpoint_configuration_type    = private # regional
method                                = "POST"
dependency_list                       = var.api_gw_dependency_list
# api_gw_region =

# Lambda
lambda_function_name = "paracord-test-lambda-dev"
lambda_description = "e2e encrypted p2p msg app function"
lambda_timeout = 5
lambda_memory_size = 256

ecr_repo        = "paracord-lambda"
create_ecr_repo = true
lambda_image_tag       = "1.0"
source_path     = "context"
is_test = false

# Dynamodb
dynamodb_table_properties = [
    { 
      name = "Enclaves"
      read_capacity = 3,
      write_capacity = 3,
      hash_key = "id"
      # range_key = ""
      stream_enabled = "true"
      stream_view_type = "NEW_IMAGE"
    },
    {
      name = "Shards",
      read_capacity = 3,
      write_capacity = 3,
      hash_key = "KEY"
      range_key = ""
      stream_enabled = "true"
      stream_view_type = "NEW_IMAGE"
    }
  ]
  
  dynamodb_table_attributes = [[
    {
      name = "id"
      type = "S"
    },
    {
        name = "sigblock"
        type = "S"
    },
    {
        name = "type"
        type = "N"
    },
    {
        name = "body"
        type = "B"
    },
    ],[
    {
      name = "id"
      type = "HASH"
    },
    {
      name = "id_attach"
      type = "RANGE"
    },
    {
      name = "burn_at"
      type = "RANGE"
    },
   ]]
   
#    dynamodb_table_secondary_index = [[
#     {
#       name               = "GameTitleIndex"
#       hash_key           = "GameTitle"
#       range_key          = "TopScore"
#       write_capacity     = 10
#       read_capacity      = 10
#       projection_type    = "INCLUDE"
#       non_key_attributes = ["UserId"]
#     }
#    ]]
   
   dynamodb_policy_action_list = ["dynamodb:PutItem", "dynamodb:DescribeTable", "dynamodb:DeleteItem", "dynamodb:GetItem", "dynamodb:Scan", "dynamodb:Query"]
   dynamodb_table_ttl = [[
      {
        attribute_name = "ttl"
        enabled = true
      }
   ]]
       
  #Tags
  tags = {
    project = "Paracord"
    managedby = "Terraform"
  }
  
  #Lambda Environment variables
  environment_variables = {
    NODE_ENV = "development"
  }

# ecr_repo_lifecycle_policy = {
# }

image_tag = "v1"
path_to_dockerfile = "../app"