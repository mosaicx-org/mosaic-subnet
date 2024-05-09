from mosaic_subnet.base.config import MosaicBaseSettings
from typing import List


class ValidatorSettings(MosaicBaseSettings):
    host: str = "0.0.0.0"
    port: int = 0
    iteration_interval: int = 60
