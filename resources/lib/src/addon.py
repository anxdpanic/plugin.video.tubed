# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .api import API
from .constants import MODES
from .lib.context import Context
from .lib.routing import Router
from .lib.url_utils import parse_query

CONTEXT = Context()

router = Router()


@router.route(MODES.MAIN)
def _main_menu():
    from .routes import main_menu  # pylint: disable=import-outside-toplevel
    main_menu.invoke(CONTEXT)


def invoke(argv):
    global CONTEXT  # pylint: disable=global-statement

    CONTEXT.argv = argv
    CONTEXT.handle = argv[1]
    CONTEXT.query = parse_query(argv[2])

    CONTEXT.api = API()

    router.invoke(CONTEXT.query)
