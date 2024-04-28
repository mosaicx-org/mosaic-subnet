from mosaic_subnet.base.config import MosaicBaseSettings
from typing import List


class MinerSettings(MosaicBaseSettings):
    host: str
    port: int
    model: str = "stabilityai/sdxl-turbo"
