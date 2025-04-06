from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
)

from aws_cdk import aws_lambda_python_alpha as lambda_python
from constructs import Construct

class SemanticRouterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add FAISS index and labels, and FAISS and Numpy package as Lambda layer
        faiss_layer = lambda_python.PythonLayerVersion(
            self, "FAISSLayer",
            entry="faiss_layer",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Lambda layer with FAISS and referernce embeddings"
        )

        # Create Lambda function
        router_lambda = _lambda.Function(
            self, "RouterLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(300),
            memory_size=1024,
            layers=[faiss_layer]
        )

        # Grant Lambda function permissions to use Amazon Bedrock
        router_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=[
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                f"arn:aws:bedrock:{Stack.of(self).region}::foundation-model/amazon.titan-embed-text-v2:0"
            ]
        ))

         # Create API Gateway
        api = apigw.RestApi(
            self, "SemanticRouterApi",
            rest_api_name="Semantic Router API",
            description="API for Semantic Router",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=[
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                    'X-Amz-Security-Token'
                ]
            ),
            deploy_options=apigw.StageOptions(
                stage_name="dev"
            )            
        )

        # Create API key
        api_key = api.add_api_key("SemanticRouterApiKey")
        
        # Create usage plan
        plan = api.add_usage_plan("SemanticRouterUsagePlan",
            name="Standard",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,
                burst_limit=2
            )
        )
        plan.add_api_key(api_key)

        # Create API Gateway integration
        integration = apigw.LambdaIntegration(router_lambda)

        # Create request validator for both body and parameters (headers)
        validator = apigw.RequestValidator(
            self, "ApiRequestValidator",
            rest_api=api,
            validate_request_body=True,
            validate_request_parameters=True
        )

        # Define a model for request validation
        request_model = api.add_model("RequestModel",
            content_type="application/json",
            model_name="RequestModel",
            schema=apigw.JsonSchema(
                schema=apigw.JsonSchemaVersion.DRAFT4,
                title="requestModel",
                type=apigw.JsonSchemaType.OBJECT,
                required=["question"],
                properties={
                    "question": apigw.JsonSchema(type=apigw.JsonSchemaType.STRING)
                }
            )
        )

        # Add resource and method to API Gateway
        resource = api.root.add_resource("ask")
        resource.add_method(
            "POST", 
            integration, 
            api_key_required=True,
            request_validator=validator,
            request_models={"application/json": request_model},
            request_parameters={
                "method.request.header.x-api-key": True,  # Make x-api-key header required
                "method.request.header.Content-Type": True  # Make Content-Type header required
            }
        )

        # Apply the usage plan to the API stage
        plan.add_api_stage(
            stage=api.deployment_stage
        )

        # Output the API key (for demonstration purposes - in production, use Secrets Manager)
        from aws_cdk import CfnOutput
        CfnOutput(self, "ApiId", value=api.rest_api_id, description="API ID")
        CfnOutput(self, "ApiKeyID", value=api_key.key_id, description="API Key ID")
