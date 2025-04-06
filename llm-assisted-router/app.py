#!/usr/bin/env python3
import aws_cdk as cdk
from llm_assisted_router.llm_assisted_router_stack import LlmAssistedRouterStack

app = cdk.App()
LlmAssistedRouterStack(app, "LlmAssistedRouterStack")
app.synth()