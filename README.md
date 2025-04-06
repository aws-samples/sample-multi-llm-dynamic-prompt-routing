# Multi-LLM dynamic prompt routing samples

**The provided code in this repository is meant to be used in a development environment. Before migrating any of the provided solutions to production, we recommend following the [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected)**

Read the accompanied blog post: https://aws.amazon.com/blogs/machine-learning/multi-llm-routing-strategies-for-generative-ai-applications-on-aws/ 

## Overview

This repository provides sample implementations for dynamic routing of user prompts across multiple Large Language Models (LLMs). The core functionality lies in the routing logic, which accurately interprets user prompts, maps them to predefined task categories, and directs them to the most appropriate LLM for response generation. You can use these samples as a starting point to build your own custom routing solution tailored to your specific needs.

The repository contains two different approaches to implement dynamic prompt routing:

1. **LLM-assisted routing**: Uses a classifier LLM to analyze prompts and make routing decisions
2. **Semantic routing**: Employs semantic search to match prompts with the most appropriate LLM

For demonstration purposes, the samples use Amazon Bedrock as the LLM provider, but can be adapted to work with other LLM providers as well.

## Content

- [LLM-assisted routing](llm-assisted-router/README.md) - Sample implementation of routing layer with the help of a classifier LLM.
- [Semantic routing](semantic-router/README.md) - Sample implementation of routing layer using semantic search.
- [Reference index generation for semantic routing](generate-faiss-reference-index/README.md) - Code for generating a [FAISS](https://github.com/facebookresearch/faiss) reference index for use in the semantic routing solution.

## Contributing

We welcome community contributions! Please ensure your sample aligns with  [AWS best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

