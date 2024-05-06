from typing import Annotated
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.getcwd())

import typer
from loguru import logger
from communex.compat.key import classic_load_key

cli = typer.Typer()


@dataclass
class ExtraCtxData:
    use_testnet: bool


@cli.callback()
def main(
    ctx: typer.Context,
    testnet: Annotated[
        bool, typer.Option(envvar="COMX_USE_TESTNET", help="Use testnet endpoints.")
    ] = False,
    log_level: str = "INFO",
):
    logger.remove()
    logger.add(sys.stdout, level=log_level.upper())

    if testnet:
        logger.info("use testnet")
    else:
        logger.info("use mainnet")

    ctx.obj = ExtraCtxData(use_testnet=testnet)


@cli.command("validator")
def validator(
    ctx: typer.Context,
    commune_key: Annotated[
        str, typer.Argument(help="Name of the key present in `~/.commune/key`")
    ],
    call_timeout: int = 30,
    iteration_interval: int = 60,
):
    from mosaic_subnet.validator import Validator, ValidatorSettings

    settings = ValidatorSettings(
        use_testnet=ctx.obj.use_testnet,
        iteration_interval=iteration_interval,
        call_timeout=call_timeout,
    )
    validator = Validator(key=classic_load_key(commune_key), settings=settings)
    validator.validation_loop()


@cli.command("miner")
def miner(
    ctx: typer.Context,
    commune_key: Annotated[
        str, typer.Argument(help="Name of the key present in `~/.commune/key`")
    ],
    host: Annotated[
        str,
        typer.Argument(
            help="the public ip you've registered, you can simply put 0.0.0.0 here to allow all incoming requests"
        ),
    ],
    port: Annotated[int, typer.Argument(help="port")],
    testnet: bool = False,
):
    from mosaic_subnet.miner import Miner, MinerSettings

    settings = MinerSettings(use_testnet=ctx.obj.use_testnet, host=host, port=port)
    miner = Miner(key=classic_load_key(commune_key), settings=settings)
    miner.serve()


@cli.command("gateway")
def gateway(
    ctx: typer.Context,
    commune_key: Annotated[
        str, typer.Argument(help="Name of the key present in `~/.commune/key`")
    ],
    host: Annotated[str, typer.Argument(help="host")],
    port: Annotated[int, typer.Argument(help="port")],
    testnet: bool = False,
    call_timeout: int = 65,
):
    import uvicorn
    from mosaic_subnet.gateway import app, Gateway, GatewaySettings

    settings = GatewaySettings(
        use_testnet=ctx.obj.use_testnet, host=host, port=port, call_timeout=call_timeout
    )
    app.m = Gateway(key=classic_load_key(commune_key), settings=settings)
    app.m.start_sync_loop()
    uvicorn.run(app=app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    cli()
