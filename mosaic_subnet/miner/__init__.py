from communex.module.module import Module
from communex.client import CommuneClient
from communex.module.client import ModuleClient
from communex.compat.key import check_ss58_address
from communex.types import Ss58Address
from substrateinterface import Keypair
from communex.key import generate_keypair
from communex.compat.key import classic_load_key
from communex._common import get_node_url

from mosaic_subnet.miner.model import DiffUsers
from mosaic_subnet.miner._config import MinerSettings
from mosaic_subnet.base.utils import get_netuid
import sys

from loguru import logger


class Miner(DiffUsers):
    def __init__(self, key: Keypair, settings: MinerSettings = None) -> None:
        super().__init__()
        self.settings = settings or MinerSettings()
        self.key = key
        self.c_client = CommuneClient(
            get_node_url(use_testnet=self.settings.use_testnet)
        )
        self.netuid = get_netuid(self.c_client)

    def serve(self):
        from communex.module.server import ModuleServer
        import uvicorn

        ## TODO: enable subnets_whitelist when comx update their key checking
        # server = ModuleServer(self, self.key, subnets_whitelist=[self.netuid])
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
