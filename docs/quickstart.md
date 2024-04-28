# Quick Start
our netuid on commune:
* mainnet: 14
* testnet: 13

## Hardware Requirements
* GPU: >= 16GB VRAM
* Storage: >= 50GB

## System Requirements
* NVIDIA GPU Driver installed
* CUDA >= 12.2
* Python >= 3.10

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

## Register a module
```
comx module register <module-name> <key> --netuid=<netuid> --ip=<ip> --port=<port>
```
if you want run it on testnet, add `--testnet` argument.
ip should be your external ip.

## Stake (validator required)
```
comx balance stake <key> <token-amount> <your_ss58_address> --netuid=<netuid>
```
if you want run it on testnet, add `--testnet` argument.

## Setup
if you want run it on testnet, add `--testnet` argument.

### Miner Setup
```bash
python mosaic_subnet/cli.py miner <your_commune_key> <host> <port>
```

### Validator Setup
```bash
python mosaic_subnet/cli.py validator <your_commune_key>
```

### Gateway Setup
ATTENTION: You must be an validator in order to run gateway
```bash
python mosaic_subnet/cli.py gateway <your_commune_key> <host> <port>
```

#### API Docs
The docs site will be available on `http://<your-ip>:<port>/docs`.



