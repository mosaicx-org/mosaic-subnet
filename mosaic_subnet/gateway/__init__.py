import asyncio
import random
import threading
import time
import concurrent.futures

import uvicorn
from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from loguru import logger
from substrateinterface import Keypair
from communex.types import Ss58Address
from communex.module.client import ModuleClient

from mosaic_subnet.base import SampleInput, BaseValidator
from mosaic_subnet.base.utils import (
    get_netuid,
)
from mosaic_subnet.gateway._config import GatewaySettings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Gateway(BaseValidator):
    def __init__(self, key: Keypair, settings: GatewaySettings) -> None:
        super().__init__()
        self.settings = settings or GatewaySettings()
        self.c_client = CommuneClient(
            get_node_url(use_testnet=self.settings.use_testnet)
        )
        self.key = key
        self.netuid = get_netuid(self.c_client)
        self.call_timeout = self.settings.call_timeout
        self.top_miners = {}
        self.validators: dict[int, tuple[list[str], Ss58Address]] = {
            2: (
                ["35.182.244.107", "7000"],
                "5DofQSnXnWjF1VUzYVzTQV658GeBExrVFEQ5B4k8Tr1LcBzb",
            )
        }
        self.sync()

    def sync(self):
        logger.info("fetching top miners...")
        self.top_miners = self.get_top_weights_miners(16)
        logger.info("top miners: {}", self.top_miners)

    def sync_loop(self):
        while True:
            time.sleep(60)
            self.sync()

    def start_sync_loop(self):
        logger.info("start sync loop")
        self._loop_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self._loop_thread.start()

    def get_top_miners(self):
        return self.top_miners

    def get_validator_weights_history(self, validator_info):
        connection, validator_key = validator_info
        module_ip, module_port = connection
        logger.debug(f"Call {validator_key} - {module_ip}:{module_port}")
        client = ModuleClient(host=module_ip, port=int(module_port), key=self.key)
        result = asyncio.run(
            client.call(
                fn="get_weights_history",
                target_key=validator_key,
                params={},
                timeout=10,
            )
        )
        return result

    def get_all_validators_weights_history(self):
        rv = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(
                self.get_validator_weights_history, self.validators.values()
            )
            validator_answers = [*it]

        for uid, response in zip(self.validators.keys(), validator_answers):
            rv.append({"uid": uid, "weights_history": response})
        return rv


@app.post(
    "/generate",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def generate_image(req: SampleInput):
    top_miners = list(app.m.get_top_miners().values())
    top_miners = random.sample(top_miners, 5)
    tasks = [
        app.m.get_miner_generation_async(miner_info, req) for miner_info in top_miners
    ]
    for future in asyncio.as_completed(tasks):
        result = await future
        if result:
            return Response(content=result, media_type="image/png")
    return Response(content=b"", media_type="image/png")


@app.get("/weights")
async def get_all_validators_weights_history():
    return app.m.get_all_validators_weights_history()


if __name__ == "__main__":
    settings = GatewaySettings(
        host="0.0.0.0",
        port=9009,
        use_testnet=True,
    )
    app.m = Gateway(key=classic_load_key("mosaic-validator0"), settings=settings)
    app.m.start_sync_loop()
    uvicorn.run(app=app, host=settings.host, port=settings.port)
