from communex.client import CommuneClient
from communex.types import Ss58Address
from communex._common import get_node_url
from substrateinterface import Keypair
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from communex.compat.key import classic_load_key
from pydantic import BaseModel
from typing import Optional

import uvicorn

from mosaic_subnet.base.utils import (
    get_netuid,
)
from mosaic_subnet.base import SampleInput, BaseValidator
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


@app.post(
    "/generate",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
def generate_image(req: SampleInput):
    result = b""
    for mid, module in app.m.get_top_weights_miners(3).items():
        result = app.m.get_miner_generation(module, req)
        if result:
            break
    return Response(content=result, media_type="image/png")


if __name__ == "__main__":
    settings = GatewaySettings(
        host="0.0.0.0",
        port=9009,
        use_testnet=True,
    )
    app.m = Gateway(key=classic_load_key("mosaic-validator0"), settings=settings)
    uvicorn.run(app=app, host=settings.host, port=settings.port)
