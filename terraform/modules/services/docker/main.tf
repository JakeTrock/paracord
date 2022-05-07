resource "random_pet" "this" {
  length = 2
}

resource "docker_image" "lambda_image" {
  name = var.lambda_image_name
  build {
    path = var.path_to_dockerfile
    tag = var.lambda_image_tag
    build_arg = var.lambda_image_build_args
    label = var.labels
  }
  depends_on = [
    module.ecr
  ]
}
