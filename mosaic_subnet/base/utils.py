import re
from dataclasses import dataclass, asdict

from communex.client import CommuneClient
from substrateinterface import Keypair
from communex.module.client import ModuleClient
from communex.compat.key import check_ss58_address
from communex.types import Ss58Address

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
            print("use netuid:", netuid)
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


def set_weights(
    score_dict: dict[int, float], netuid: int, client: CommuneClient, key: Keypair
) -> None:
    print("set weights", score_dict)
    uids = []
    weights = []
    for uid, score in score_dict.items():
        uids.append(uid)
        weights.append(score)
    client.vote(key=key, uids=uids, weights=weights, netuid=netuid)
