#!/usr/bin/env python3
import aws_cdk as cdk
from semantic_router.semantic_router_stack import SemanticRouterStack

app = cdk.App()
SemanticRouterStack(app, "SemanticRouterStack")
app.synth()