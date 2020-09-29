# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .api import API
from .constants import SCRIPT_MODES
from .lib.context import Context
from .lib.routing import Router
from .lib.url_utils import parse_script_query

# pylint: disable=import-outside-toplevel

CONTEXT = Context()

router = Router()


@router.route(SCRIPT_MODES.MAIN)
def _main():
    return


@router.route(SCRIPT_MODES.SEARCH_HISTORY)
def _search_history():
    from .scripts import search_history
    search_history.invoke(CONTEXT)


@router.route(SCRIPT_MODES.CONFIGURE_REGIONAL)
def _configure_regional():
    from .scripts import configure_regional
    configure_regional.invoke(CONTEXT)


@router.route(SCRIPT_MODES.CONFIGURE_SUBTITLES)
def _configure_subtitles():
    from .scripts import configure_subtitles
    configure_subtitles.invoke(CONTEXT)


def invoke(argv):
    global CONTEXT  # pylint: disable=global-statement

    CONTEXT.argv = argv
    CONTEXT.handle = -1
    CONTEXT.query = parse_script_query(CONTEXT.argv[1])
    CONTEXT.mode = CONTEXT.query.get('mode', str(SCRIPT_MODES.MAIN))

    CONTEXT.api = API(
        language=CONTEXT.settings.language,
        region=CONTEXT.settings.region
    )

    router.invoke(CONTEXT.query)
