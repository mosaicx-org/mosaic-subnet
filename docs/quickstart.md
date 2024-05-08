# Quick Start

Our netuid on commune:

* mainnet: 14
* testnet: 13

If you want run it on testnet, add `--testnet` argument after `comx`.

## Hardware Requirements
* Memory: >= 16GB
* GPU: >= 16GB VRAM
* Storage: >= 50GB

## System Requirements

* NVIDIA GPU Driver installed
* CUDA >= 12.2
* Python >= 3.10
* [comx](https://github.com/agicommies/communex) cli tool for commune key management

## Register a module
```
comx module register <module-name> <key> --netuid=<netuid> --ip=<ip> --port=<port>
```

IP should be your public ip.

## Stake (validator required)
```
comx balance stake <key> <token-amount> <your_ss58_address> --netuid=<netuid>
```

## Running with Docker (Recommended)
We recommend you to use Docker to run the miner and validator. The deployment in this method can make the services more robust and enable automatic upgrades.

### Prerequisites
You need to install the following components to meet the requirements for running the mosaic containers.
* Docker https://docs.docker.com/engine/install/ubuntu/
* NVIDIA GPU Driver
* NVIDIA container toolkit https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

### Setup miner with docker
```bash
docker run --gpus=all -d --network host --restart always \
-v $HOME/.commune:/root/.commune \
-v $HOME/.cache/huggingface:/root/.cache/huggingface \
--name mosaic-miner \
mos4ic/mosaic-subnet:latest \
python mosaic_subnet/cli.py [--testnet] [--log-level=INFO] miner <your_commune_key> <host> <port>
```
host should be 0.0.0.0 so it allows all the incoming requests with other ip and for the local testing use 127.0.0.1

### Setup validator with docker
```bash
docker run --gpus=all -d --network host --restart always \
-v $HOME/.commune:/root/.commune \
-v $HOME/.cache/huggingface:/root/.cache/huggingface \
--name mosaic-validator \
mos4ic/mosaic-subnet:latest \
python mosaic_subnet/cli.py [--testnet] [--log-level=INFO] validator <your_commune_key>
```
host should be 0.0.0.0 so it allows all the incoming requests with other ip and for the local testing use 127.0.0.1
### Enable auto upgrade
This component will periodically check the latest mosaic docker image, pull it and restart the running containers with the new image.
```bash
docker run -d \
--name watchtower \
-v /var/run/docker.sock:/var/run/docker.sock \
containrrr/watchtower --interval 300 mosaic-miner mosaic-validator 
```

## Running with source code
## Installation
[Install Poetry](https://python-poetry.org/docs/) if you don't have it.

After that, run the following commands:

```
# clone this project
git clone https://github.com/mosaicx-org/mosaic-subnet
cd mosaic-subnet

# start virtualenv and enter it
poetry shell

# install dependencies
poetry install
```

### Miner Setup
```bash
python mosaic_subnet/cli.py [--testnet] [--log-level=INFO] miner <your_commune_key> <host> <port>
```
host should be `0.0.0.0` so it allows all the incoming requests with other ip and for the local testing use `127.0.0.1`

### Validator Setup

```bash
python mosaic_subnet/cli.py [--testnet] [--log-level=INFO] validator <your_commune_key> [host] [port]
```

### Gateway Setup

ATTENTION: You must be a validator in order to run gateway

```bash
python mosaic_subnet/cli.py [--testnet] [--log-level=INFO] gateway <your_commune_key> <host> <port>
```

The docs site will be available on `http://<your-ip>:<port>/docs`.