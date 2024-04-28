# Mosaic Subnet
Mosaic is an open platform for generative artificial intelligence. Users can generate images from natural language descriptions using modules provided by [Commune AI](https://communeai.org/).


## Design
Within the Commune subnet, Mosaic endeavors to foster greater engagement among model developers in the image AIGC network through equitable incentivization mechanisms. Additionally, the aim is to enhance accessibility to these exemplary AI models for a broader user base via API integration and a dedicated web application.

<img width="985" alt="image" src="https://github.com/montecarlo-labs/mosaic-subnet/assets/6276527/184aac61-4cd0-4372-b195-e700d5f0b801">

Within the Mosaic subnet, two distinct task categories exist:
- The first entails requests originating from the application layer, routed through an HTTP gateway for subsequent processing by validators.
- The second involves prompts sourced from datasets, intended for ongoing task dissemination to miners for computation and validation during periods of system idleness.

The validator will extract the embedding vectors from the text prompt and the generated image, then employ cosine similarity to assess the likeness between the two embedding vectors. This allows us to ascertain whether the generated image aligns with the descriptive content of the prompt text.

## Roadmap
- v1.0: Implement a foundational image generation network, integrating cosine similarity for image-text validation and reward distribution.
- v1.1: Introduce support for Web + API + Bot, enabling direct utilization of subnet model outputs through a web interface.
- v1.2: Enhance scheduling algorithms to optimize user experience and service reliability for web app operations.
- v1.3: Enable fine-tuning capabilities and decouple miners from validators through integration with a model registry.

## Running
Please refer to [Quick Start Guide](docs/quickstart.md)
