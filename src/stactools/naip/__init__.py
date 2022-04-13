# flake8: noqa

import stactools.core

from stactools.naip.stac import create_item

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.naip import commands

    registry.register_subcommand(commands.create_naip_command)


__version__ = "0.1.6"
