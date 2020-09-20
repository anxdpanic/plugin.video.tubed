# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from .constants import MODES
from .lib.routing import Router
from .lib.utils import parse_query

router = Router()


@router.route(MODES.MAIN)
def _main_menu():
    from .routes import main_menu  # pylint: disable=import-outside-toplevel
    main_menu.invoke()


def invoke(argv):
    query = parse_query(argv[2])
    mode = query.get('mode')

    router.invoke(mode, query)
