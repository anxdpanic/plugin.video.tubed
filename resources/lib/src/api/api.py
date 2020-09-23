# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import tubed_api  # pylint: disable=import-error

from ..constants import CREDENTIALS
from ..constants import ONE_MINUTE
from ..constants import ONE_WEEK
from ..exceptions.decorators import catch_api_exceptions
from ..lib import memoizer


class API:
    access_token = ''

    def __init__(self, language='en-US', region='US'):
        self._language = language
        self._region = region

        self._api = tubed_api

        self._api.CLIENT_ID = CREDENTIALS.ID
        self._api.CLIENT_SECRET = CREDENTIALS.SECRET
        self._api.API_KEY = CREDENTIALS.KEY

        self._api.ACCESS_TOKEN = self.access_token

        self._client = self._api.oauth.Client
        self._usher = self._api.usher
        self.api = self._api.v3

    @property
    def language(self):
        return self._language.replace('-', '_')

    @language.setter
    def language(self, value):
        self._language = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        self._region = value

    @memoizer.cache_method(limit=ONE_MINUTE * 5)
    def resolve(self, video_id, quality=None):
        if isinstance(quality, (int, str)):
            quality = self._usher.Quality(quality)

        return self._usher.resolve(video_id, quality=quality,
                                   language=self.language, region=self.region)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_WEEK)
    def languages(self):

        return self.api.i18n_languages.get({
            'part': 'snippet',
            'hl': self.language
        })

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_WEEK)
    def regions(self):

        return self.api.i18n_regions.get({
            'part': 'snippet',
            'hl': self.region
        })
