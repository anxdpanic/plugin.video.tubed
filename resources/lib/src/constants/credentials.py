# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from base64 import b64decode
from enum import Enum


class CREDENTIALS(Enum):
    KEY = b64decode('QUl6YVN5QUR0T0RKVTB4d3BXdWZfbUE1N3VFdUNwT0FfcjN6WEtv')
    ID = b64decode('OTAxOTQ1MDk2MjU2LWV2MGk5dmFuczd0Z25iYTRtNjZjaTQ2ZGFnc3RlY2Y1')
    SECRET = b64decode('Y2RMSldUdHdrWENod2ZsV1dqYnNwYVNH')
    TOKEN = ''
