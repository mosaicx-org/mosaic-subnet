import time
import asyncio
import concurrent.futures
import time
from functools import partial

from dataclasses import dataclass
from PIL import UnidentifiedImageError
from communex.module.module import Module
from communex.client import CommuneClient
from communex.module.client import ModuleClient
from communex.compat.key import check_ss58_address
from communex.types import Ss58Address
from substrateinterface import Keypair
from communex.key import generate_keypair
from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import classic_load_key

from mosaic_subnet.validator._config import ValidatorSettings
from mosaic_subnet.validator.model import CLIP
from mosaic_subnet.base.utils import get_netuid, set_weights
from mosaic_subnet.base import SampleInput, BaseValidator
from mosaic_subnet.validator.dataset import ValidationDataset


class Validator(BaseValidator, Module):
    def __init__(self, key: Keypair, settings: ValidatorSettings = None) -> None:
        super().__init__()
        self.settings = settings or ValidatorSettings()
        self.key = key
        self.c_client = CommuneClient(
            get_node_url(use_testnet=self.settings.use_testnet)
        )
        self.netuid = get_netuid(self.c_client)
        self.model = CLIP()
        self.dataset = ValidationDataset()
        self.call_timeout = self.settings.call_timeout

    def calculate_score(self, img: bytes, prompt: str):
        try:
            return self.model.get_similarity(img, prompt)
        except Exception:
            return 0

    async def validate_step(self):
        score_dict = dict()
        modules_info = self.get_queryable_miners()
    
        input = self.get_validate_input()
        print("input:", input)
        get_miner_generation = partial(self.get_miner_generation, input=input)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(get_miner_generation, modules_info.values())
            miner_answers = [*it]

        for uid, miner_response in zip(modules_info.keys(), miner_answers):
            miner_answer = miner_response
            if not miner_answer:
                print(f"Skipping miner {uid} that didn't answer")
                continue
            score = self.calculate_score(miner_answer, input.prompt)
            score_dict[uid] = score
        
        if not score_dict:
            print("score_dict empty, skip set weights")
            return
        try:
            set_weights(
                score_dict=score_dict,
                netuid=self.netuid,
                client=self.c_client,
                key=self.key,
            )
        except Exception as e:
            print("ERROR", e)

    def get_validate_input(self):
        return SampleInput(
            prompt=self.dataset.random_prompt(),
            steps=2,
        )

    def validation_loop(self) -> None:
        settings = self.settings
        while True:
            start_time = time.time()
            asyncio.run(self.validate_step())
            elapsed = time.time() - start_time
            if elapsed < settings.iteration_interval:
                sleep_time = settings.iteration_interval - elapsed
                print(f"Sleeping for {sleep_time}")
                time.sleep(sleep_time)


if __name__ == "__main__":
    settings = ValidatorSettings(use_testnet=True)
    Validator(
        key=classic_load_key("mosaic-validator0"), settings=settings
    ).validation_loop()
