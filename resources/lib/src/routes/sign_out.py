# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmc  # pylint: disable=import-error

from ..storage.users import UserStorage

USERS = UserStorage()


def invoke(context):
    context.api.revoke_token()

    xbmc.executebuiltin('Container.Refresh')

    # TODO: clear caches
