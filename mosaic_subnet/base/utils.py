import re

from communex.client import CommuneClient
from loguru import logger

IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")


def extract_address(string: str):
    """
    Extracts an address from a string.
    """
    return re.search(IP_REGEX, string)


def get_netuid(client: CommuneClient, subnet_name: str = "mosaic"):
    subnets = client.query_map_subnet_names()
    for netuid, name in subnets.items():
        if name == subnet_name:
            logger.info(f"use netuid: {netuid}")
            return netuid
    raise ValueError(f"Subnet {subnet_name} not found")


def get_ip_port(modules_addresses: dict[int, str]):
    filtered_addr = {
        id: extract_address(addr) for id, addr in modules_addresses.items()
    }
    ip_port = {
        id: x.group(0).split(":") for id, x in filtered_addr.items() if x is not None
    }
    return ip_port
