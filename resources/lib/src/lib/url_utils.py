# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from copy import deepcopy
from urllib.parse import parse_qs
from urllib.parse import urlencode

from ..constants import ADDON_ID


def parse_query(query):
    payload = {
        'mode': 'main'
    }

    args = parse_qs(query.lstrip('?'))

    for arg in args:
        if len(args[arg]) == 1:
            payload[arg] = args[arg][0]

        else:
            payload[arg] = args[arg]

    return payload


def create_addon_path(path='/', parameters=None):
    if not parameters:
        parameters = {}

    path = 'plugin://%s/%s' % (ADDON_ID, path.rstrip('/') + '/')

    if len(parameters) > 0:
        url_parameters = deepcopy(parameters)

        for parameter in url_parameters:
            if isinstance(parameters[parameter], int):
                parameters[parameter] = str(parameters[parameter])

            url_parameters[parameter] = parameters[parameter]

        return '?'.join([path, urlencode(url_parameters)])

    return path
