# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

from ..constants import ONE_WEEK
from ..storage.data_cache import DataCache
from . import utils


def get_cached(endpoint, content_ids, parameters=None, cache_ttl=4):
    cache = DataCache()

    payload = {}

    cached_ids = []
    uncached_ids = []

    cached_content = cache.get_items(ONE_WEEK * cache_ttl, content_ids)
    for content_id in content_ids:
        if not cached_content.get(content_id):
            uncached_ids.append(content_id)
        else:
            cached_ids.append(content_id)

    payload.update(cached_content)

    if len(uncached_ids) > 0:
        uncached_data = {}

        if parameters and isinstance(parameters, dict):
            api_payload = endpoint(uncached_ids, **parameters)
        else:
            api_payload = endpoint(uncached_ids)

        items = api_payload.get('items', [])
        for item in items:
            content_id = str(item['id'])
            uncached_data[content_id] = item
            payload[content_id] = item

        cache.set_all(uncached_data)

    return payload


def get_fanart(endpoint, channel_ids, cache_ttl=4):
    channel_ids = list(set(channel_ids))

    channels = get_cached(endpoint, channel_ids, cache_ttl)

    payload = {}
    for channel_id, channel in channels.items():
        payload[channel_id] = utils.get_fanart(channel.get('brandingSettings', {}))

    return payload
