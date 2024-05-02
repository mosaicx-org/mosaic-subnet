from communex.module.module import Module
from communex.client import CommuneClient
from communex.module.client import ModuleClient
from communex.compat.key import check_ss58_address
from communex.types import Ss58Address
from substrateinterface import Keypair
from communex.key import generate_keypair
from communex.compat.key import classic_load_key

from mosaic_subnet.miner.model import DiffUsers
from mosaic_subnet.miner._config import MinerSettings

import sys

from loguru import logger

class Miner(DiffUsers):
    def __init__(self, key: Keypair, settings: MinerSettings = None) -> None:
        super().__init__()
        self.settings = settings or MinerSettings()
        self.key = key

    def serve(self):
        from communex.module.server import ModuleServer
        import uvicorn
        server = ModuleServer(self, self.key)
        app = server.get_fastapi_app()
        uvicorn.run(app, host=self.settings.host, port=self.settings.port)


if __name__ == "__main__":
    settings = MinerSettings(
        host="0.0.0.0",
        port=7777,
        use_testnet=True,
    )
    Miner(key=classic_load_key("mosaic-miner0"), settings=settings).serve()
