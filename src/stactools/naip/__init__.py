# flake8: noqa

import stactools.core

stactools.core.use_fsspec()


def register_plugin(registry):
    # Register subcommands

    from stactools.naip import commands

    registry.register_subcommand(commands.create_naip_command)


__version__ = "0.3.2"
