output "api_url" {
  value = element(compact(concat(tolist(["default"]), aws_api_gateway_deployment.deployment.*.invoke_url)), 0)
}

output "api_gw_id" {
  value = aws_api_gateway_rest_api.api.id
}

output "api_gw_name" {
  value = aws_api_gateway_rest_api.api.name
}

output "api_gw_root_resource_id" {
  value = aws_api_gateway_rest_api.api.root_resource_id
}

output "api_gw_api_resource_id" {
  value = aws_api_gateway_resource.api_resource.id
}

output "api_gw_message_resource_id" {
  // necessary due to Terraform's inability to evaluate one side of assertion before contiruing onward, so use tolist
  value = element(compact(concat(tolist(["default"]), aws_api_gateway_resource.messages_resource.*.id)), 0)
}