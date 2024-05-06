import asyncio
import concurrent.futures
import time
from functools import partial

from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import classic_load_key
from communex.module.module import Module
from loguru import logger
from substrateinterface import Keypair

from mosaic_subnet.base import SampleInput, BaseValidator
from mosaic_subnet.base.utils import get_netuid
from mosaic_subnet.validator._config import ValidatorSettings
from mosaic_subnet.validator.dataset import ValidationDataset
from mosaic_subnet.validator.model import CLIP
from mosaic_subnet.validator.utils import normalize_score


class Validator(BaseValidator, Module):
    def __init__(self, key: Keypair, settings: ValidatorSettings | None = None) -> None:
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
        logger.debug("input:", input)
        get_miner_generation = partial(
            self.get_miner_generation_with_elapsed, input=input
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            it = executor.map(get_miner_generation, modules_info.values())
            miner_answers = [*it]

        for uid, miner_response in zip(modules_info.keys(), miner_answers):
            miner_answer, elapsed = miner_response
            logger.debug(f"uid {uid} elapsed time: {elapsed}")
            if not miner_answer:
                logger.debug(f"Skipping miner {uid} that didn't answer")
                continue
            score = self.calculate_score(miner_answer, input.prompt)
            score_dict[uid] = score

        if not score_dict:
            logger.info("score_dict empty, skip set weights")
            return

        logger.debug("original scores:", score_dict)
        normalized_scores = normalize_score(score_dict=score_dict)
        logger.debug("normalized scores:", normalized_scores)

        score_sum = sum(normalized_scores.values())

        weighted_scores: dict[int, int] = {}
        for uid, score in normalized_scores.items():
            weight = int(score * 1000 / score_sum)
            if weight > 0:
                weighted_scores[uid] = weight

        logger.debug("weighted scores:", weighted_scores)
        if not weighted_scores:
            logger.info("weighted_scores empty, skip set weights")
            return
        try:
            uids = list(weighted_scores.keys())
            weights = list(weighted_scores.values())
            logger.info("Setting weights for {count} uids", count=len(uids))
            logger.debug(f"Setting weights for the following uids: {weighted_scores}")
            self.c_client.vote(
                key=self.key, uids=uids, weights=weights, netuid=self.netuid
            )
        except Exception as e:
            logger.error(e)

    def get_validate_input(self):
        return SampleInput(
            prompt=self.dataset.random_prompt(),
            steps=1,
        )

    def validation_loop(self) -> None:
        settings = self.settings
        while True:
            start_time = time.time()
            asyncio.run(self.validate_step())
            elapsed = time.time() - start_time
            if elapsed < settings.iteration_interval:
                sleep_time = settings.iteration_interval - elapsed
                logger.info(f"Sleeping for {sleep_time}")
                time.sleep(sleep_time)


if __name__ == "__main__":
    settings = ValidatorSettings(use_testnet=True)
    Validator(
        key=classic_load_key("mosaic-validator0"), settings=settings
    ).validation_loop()
