resource "aws_lambda_function" "{{API_NAME}}_Lambda" {
  function_name = "{{API_NAME}}_root"
  handler = "{{LAMBDA_HANDLER}}"
  runtime = "{{LAMBDA_RUNTIME}}"
  role = "${aws_iam_role.{{API_NAME}}_Role.arn}"
  timeout = {{LAMBDA_TIMEOUT}}
  memory_size = {{LAMBDA_MEMORY}}
  filename = "${path.module}/../{{LAMBDA_ZIP}}"
  source_code_hash = "${base64sha256(file("${path.module}/../{{LAMBDA_ZIP}}"))}"
}

{% for s in STAGES %}
resource "aws_lambda_permission" "with_api_gateway_{{s}}" {
  statement_id = "AllowExecutionFromApiGateway"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.{{API_NAME}}_Lambda.arn}"
  principal = "apigateway.amazonaws.com"
  source_arn = "arn:aws:execute-api:${var.region}:{{API_ACCOUNT}}:*"
  qualifier = "{{s}}"
}

resource "aws_lambda_alias" "{{s}}" {
  name = "{{s}}"
  description = "deploy"
  function_name = "${aws_lambda_function.{{API_NAME}}_Lambda.arn}"
  {%- if not STAGED %}
  function_version = "${aws_lambda_function.{{API_NAME}}_Lambda.version}"
  {%- endif %}
  {%- if STAGED %}
  function_version = "${var.{{s}}_version}"
  {%- endif %}
}
{% endfor %}
