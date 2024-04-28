from mosaic_subnet.base.config import MosaicBaseSettings
from typing import List


class GatewaySettings(MosaicBaseSettings):
    host: str
    port: int
