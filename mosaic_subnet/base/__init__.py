import asyncio
import base64
import heapq
import time
from operator import itemgetter
from typing import Optional

from communex.module.client import ModuleClient
from communex.types import Ss58Address
from loguru import logger
from pydantic import BaseModel

from .utils import get_ip_port


class SampleInput(BaseModel):
    prompt: str
    negative_prompt: str = ""
    steps: int = 1
    seed: Optional[int] = None


class BaseValidator:
    def __init__(self):
        self.call_timeout = 60

    def get_miner_generation(
            self,
            miner_info: tuple[list[str], Ss58Address],
            input: SampleInput,
    ) -> Optional[bytes]:
        try:
            connection, miner_key = miner_info
            module_ip, module_port = connection
            logger.debug(f"Call {miner_key} - {module_ip}:{module_port}")
            client = ModuleClient(host=module_ip, port=int(module_port), key=self.key)
            result = asyncio.run(
                client.call(
                    fn="sample",
                    target_key=miner_key,
                    params=input.model_dump(),
                    timeout=self.call_timeout,
                )
            )
            return base64.b64decode(result)
        except Exception as e:
            logger.debug(f"Call error: {e}")
            return None

    async def get_miner_generation_async(
            self,
            miner_info: tuple[list[str], Ss58Address],
            input: SampleInput,
    ) -> Optional[bytes]:
        try:
            connection, miner_key = miner_info
            module_ip, module_port = connection
            logger.debug(f"Call {miner_key} - {module_ip}:{module_port}")
            client = ModuleClient(host=module_ip, port=int(module_port), key=self.key)
            result = await client.call(
                fn="sample",
                target_key=miner_key,
                params=input.model_dump(),
                timeout=self.call_timeout,
            )
            return base64.b64decode(result)
        except Exception as e:
            logger.debug(f"Call error: {e}")
            return None

    def get_miner_generation_with_elapsed(
            self,
            miner_info: tuple[list[str], Ss58Address],
            input: SampleInput,
    ) -> tuple[Optional[bytes], float]:
        start = time.time()
        try:
            result = self.get_miner_generation(miner_info=miner_info, input=input)
        except Exception:
            return None, 99999
        elapsed = time.time() - start
        return result, elapsed

    def get_queryable_miners(self):
        modules_addresses = self.c_client.query_map_address(self.netuid)
        modules_keys = self.c_client.query_map_key(self.netuid)
        val_ss58 = self.key.ss58_address
        if val_ss58 not in modules_keys.values():
            raise RuntimeError(f"validator key {val_ss58} is not registered in subnet")
        modules_info: dict[int, tuple[list[str], Ss58Address]] = {}

        modules_filtered_address = get_ip_port(modules_addresses)
        for module_id in modules_keys.keys():
            if module_id == 0:  # skip master
                continue
            if modules_keys[module_id] == val_ss58:  # skip yourself
                continue
            module_addr = modules_filtered_address.get(module_id, None)
            if not module_addr:
                continue
            modules_info[module_id] = (module_addr, modules_keys[module_id])
        return modules_info

    def get_top_weights_miners(self, k: int):
        modules_weights = self.c_client.query_map_weights(netuid=self.netuid)
        weight_map = {}
        for _, weight_list in modules_weights.items():
            for uid, score in weight_list:
                v = weight_map.get(uid, 0)
                weight_map[uid] = v + score
        logger.debug(weight_map)
        candidates = heapq.nlargest(k, weight_map.items(), key=itemgetter(1))

        modules_addresses = self.c_client.query_map_address(self.netuid)
        modules_keys = self.c_client.query_map_key(self.netuid)
        val_ss58 = self.key.ss58_address
        if val_ss58 not in modules_keys.values():
            raise RuntimeError(f"validator key {val_ss58} is not registered in subnet")
        modules_info: dict[int, tuple[list[str], Ss58Address]] = {}

        modules_filtered_address = get_ip_port(modules_addresses)
        for module_id, weight in candidates:
            if modules_keys[module_id] == val_ss58:  # skip yourself
                continue
            module_addr = modules_filtered_address.get(module_id, None)
            if not module_addr:
                continue
            modules_info[module_id] = (module_addr, modules_keys[module_id])
        return modules_info

    