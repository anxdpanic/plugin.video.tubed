# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import time

import tubed_api  # pylint: disable=import-error
from tubed_api import oauth  # pylint: disable=import-error
from tubed_api import usher  # pylint: disable=import-error
from tubed_api import v3  # pylint: disable=import-error

from ..constants import CREDENTIALS
from ..constants import ONE_MINUTE
from ..constants import ONE_WEEK
from ..exceptions.decorators import catch_api_exceptions
from ..lib import memoizer
from ..storage.data_cache import DataCache
from ..storage.users import UserStorage

USERS = UserStorage()


class API:  # pylint: disable=too-many-public-methods

    def __init__(self, language='en-US', region='US'):
        self._language = language
        self._region = region
        self._max_results = 50

        self._api = tubed_api

        self._api.CLIENT_ID = str(CREDENTIALS.ID)
        self._api.CLIENT_SECRET = str(CREDENTIALS.SECRET)
        self._api.API_KEY = str(CREDENTIALS.KEY)

        self._api.ACCESS_TOKEN = USERS.access_token

        self._usher = usher

        self.quality = self._usher.Quality

        self.api = v3
        self.client = oauth.Client()
        self.refresh_token()

    @property
    def logged_in(self):
        self.refresh_token()
        return USERS.access_token and not USERS.token_expired

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

    @property
    def max_results(self):
        return int(self._max_results)

    @max_results.setter
    def max_results(self, value):
        self._max_results = int(value)

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
            'hl': self.language
        })

    @catch_api_exceptions
    def remove_playlist(self, playlist_id):
        parameters = {
            'id': playlist_id,
            'mine': 'true'
        }

        return self.api.playlists.delete(parameters=parameters)

    @catch_api_exceptions
    def rename_playlist(self, playlist_id, title, privacy_status='private'):
        parameters = {
            'part': 'snippet,id,status'
        }
        data = {
            'kind': 'youtube#playlist',
            'id': playlist_id,
            'snippet': {
                'title': title
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        return self.api.playlists.update(parameters=parameters, data=data)

    @catch_api_exceptions
    def create_playlist(self, title, privacy_status='private'):
        parameters = {
            'part': 'snippet,status'
        }
        data = {
            'kind': 'youtube#playlist',
            'snippet': {
                'title': title
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        return self.api.playlists.insert(parameters=parameters, data=data)

    @catch_api_exceptions
    def add_to_playlist(self, playlist_id, video_id):
        parameters = {
            'part': 'snippet',
            'mine': 'true'
        }
        data = {
            'kind': 'youtube#playlistItem',
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }

        return self.api.playlist_items.insert(parameters=parameters, data=data)

    @catch_api_exceptions
    def remove_from_playlist(self, playlist_item_id):

        return self.api.playlist_items.delete({
            'id': playlist_item_id
        })

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def rating(self, video_id):
        if isinstance(video_id, list):
            video_id = ','.join(video_id)

        return self.api.videos.get_rating({
            'id': video_id
        })

    @catch_api_exceptions
    def rate(self, video_id, rating='like'):
        parameters = {
            'id': video_id,
            'rating': rating
        }

        return self.api.videos.rate(parameters=parameters)

    @catch_api_exceptions
    def subscribe(self, channel_id):
        parameters = {
            'part': 'snippet'
        }
        data = {
            'kind': 'youtube#subscription',
            'snippet': {
                'resourceId': {
                    'kind': 'youtube#channel',
                    'channelId': channel_id
                }
            }
        }

        return self.api.subscriptions.insert(parameters=parameters, data=data)

    @catch_api_exceptions
    def unsubscribe(self, subscription_id):

        return self.api.subscriptions.delete({
            'id': subscription_id
        })

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def subscriptions(self, channel_id, order='alphabetical', page_token=''):
        parameters = {
            'part': 'snippet',
            'maxResults': str(self.max_results),
            'order': order
        }
        if channel_id == 'mine':
            parameters['mine'] = 'true'
        else:
            parameters['channelId'] = channel_id

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.subscriptions.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def video_category(self, category_id, page_token=''):
        parameters = {
            'part': 'snippet,contentDetails,status',
            'maxResults': str(self.max_results),
            'videoCategoryId': category_id,
            'chart': 'mostPopular',
            'regionCode': self.region,
            'hl': self.language
        }
        if page_token:
            parameters['pageToken'] = page_token

        return self.api.videos.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def video_categories(self, page_token=''):
        parameters = {
            'part': 'snippet',
            'maxResults': str(self.max_results),
            'regionCode': self.region,
            'hl': self.language
        }
        if page_token:
            parameters['pageToken'] = page_token

        return self.api.video_categories.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def channel_sections(self, channel_id):
        parameters = {
            'part': 'snippet,contentDetails',
            'regionCode': self.region,
            'hl': self.language
        }

        if channel_id == 'mine':
            parameters['mine'] = 'true'
        else:
            parameters['channelId'] = channel_id

        return self.api.channel_sections.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def playlists_of_channel(self, channel_id, page_token=''):
        parameters = {
            'part': 'snippet',
            'maxResults': str(self.max_results)
        }

        if channel_id != 'mine':
            parameters['channelId'] = channel_id
        else:
            parameters['mine'] = 'true'

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.playlists.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def playlist_items(self, playlist_id, page_token='', max_results=None):
        parameters = {
            'part': 'snippet',
            'maxResults': max_results or str(self.max_results),
            'playlistId': playlist_id
        }

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.playlist_items.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def channel_by_username(self, username):
        parameters = {
            'part': 'id'
        }

        if username == 'mine':
            parameters['mine'] = 'true'
        else:
            parameters['forUsername'] = username

        return self.api.channels.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def channels(self, channel_id):
        if isinstance(channel_id, list):
            channel_id = ','.join(channel_id)

        parameters = {
            'part': 'snippet,contentDetails,brandingSettings'
        }

        if channel_id != 'mine':
            parameters['id'] = channel_id
        else:
            parameters['mine'] = 'true'

        return self.api.channels.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def my_rating(self, rating='like', page_token=''):
        parameters = {
            'part': 'snippet,status',
            'myRating': rating,
            'maxResults': str(self.max_results)
        }

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.videos.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def videos(self, video_id, live_details=False):
        if isinstance(video_id, list):
            video_id = ','.join(video_id)

        parts = ['snippet', 'contentDetails', 'status']
        if live_details:
            parts.append('liveStreamingDetails')

        parameters = {
            'part': ','.join(parts),
            'id': video_id
        }

        return self.api.videos.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def playlists(self, playlist_id):
        if isinstance(playlist_id, list):
            playlist_id = ','.join(playlist_id)

        parameters = {
            'part': 'snippet,contentDetails',
            'id': playlist_id
        }

        return self.api.playlists.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def parent_comments(self, video_id, page_token='', max_results=None):
        parameters = {
            'part': 'snippet',
            'videoId': video_id,
            'order': 'relevance',
            'textFormat': 'plainText',
            'maxResults': max_results or str(self.max_results)
        }

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.comment_threads.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def child_comments(self, parent_id, page_token='', max_results=None):
        parameters = {
            'part': 'snippet',
            'parentId': parent_id,
            'textFormat': 'plainText',
            'maxResults': max_results or str(self.max_results)
        }

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.comments.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def channel_videos(self, channel_id, page_token=''):
        parameters = {
            'part': 'snippet',
            'hl': self.language,
            'maxResults': str(self.max_results),
            'type': 'video',
            'safeSearch': 'none',
            'order': 'date'
        }

        if channel_id == 'mine':
            parameters['forMine'] = 'true'
        else:
            parameters['channelId'] = channel_id

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.search.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def live_events(self, event_type='live', order='relevance', page_token=''):
        parameters = {
            'part': 'snippet',
            'type': 'video',
            'order': order,
            'eventType': event_type,
            'regionCode': self.region,
            'hl': self.language,
            'relevanceLanguage': self.language,
            'maxResults': str(self.max_results)
        }

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.search.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def related_videos(self, video_id, page_token='', max_results=None):
        parameters = {
            'relatedToVideoId': video_id,
            'part': 'snippet',
            'type': 'video',
            'regionCode': self.region,
            'hl': self.language,
            'maxResults': max_results or str(self.max_results)
        }

        if page_token:
            parameters['pageToken'] = page_token

        return self.api.search.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def search(self, query, search_type=None, event_type='', channel_id='',
               order='relevance', safe_search='moderate', page_token=''):
        parameters = {
            'q': query,
            'part': 'snippet',
            'regionCode': self.region,
            'hl': self.language,
            'relevanceLanguage': self.language,
            'maxResults': str(self.max_results)
        }

        if search_type is None:
            search_type = ['video', 'channel', 'playlist']

        elif not search_type:
            search_type = ''

        elif isinstance(search_type, list):
            search_type = ','.join(search_type)

        if event_type and event_type in ['live', 'upcoming', 'completed']:
            parameters['eventType'] = event_type

        if search_type:
            parameters['type'] = search_type

        if channel_id:
            parameters['channelId'] = channel_id

        if order:
            parameters['order'] = order

        if safe_search:
            parameters['safeSearch'] = safe_search

        if page_token:
            parameters['pageToken'] = page_token

        video_only = ['eventType', 'videoCaption', 'videoCategoryId', 'videoDefinition',
                      'videoDimension', 'videoDuration', 'videoEmbeddable', 'videoLicense',
                      'videoSyndicated', 'videoType', 'relatedToVideoId', 'forMine']

        for key in video_only:
            if parameters.get(key) is not None:
                parameters['type'] = 'video'
                break

        return self.api.search.get(parameters=parameters)

    @catch_api_exceptions
    @memoizer.cache_method(limit=ONE_MINUTE * 7)
    def most_popular(self, page_token=''):
        parameters = {
            'part': 'snippet,status',
            'maxResults': str(self.max_results),
            'regionCode': self.region,
            'hl': self.language,
            'chart': 'mostPopular'
        }
        if page_token:
            parameters['pageToken'] = page_token

        return self.api.videos.get(parameters=parameters)

    @memoizer.cache_method(limit=ONE_MINUTE * 5)
    def resolve(self, video_id, quality=None):
        if isinstance(quality, (int, str)):
            quality = self._usher.Quality(quality)

        return self._usher.resolve(video_id, quality=quality,
                                   language=self.language, region=self.region)

    @catch_api_exceptions
    def refresh_token(self):
        if USERS.access_token and USERS.token_expired:
            access_token, expiry = self.client.refresh_token(USERS.refresh_token)
            USERS.access_token = access_token
            USERS.token_expiry = time.time() + int(expiry)
            USERS.save()
            self.refresh_client()

    @catch_api_exceptions
    def revoke_token(self):
        if USERS.refresh_token:
            self.client.revoke_token(USERS.refresh_token)
            USERS.access_token = ''
            USERS.refresh_token = ''
            USERS.token_expiry = -1
            USERS.save()
            self.refresh_client()

    @catch_api_exceptions
    def request_codes(self):
        return self.client.request_codes()

    @catch_api_exceptions
    def request_access_token(self, device_code):
        data = self.client.request_access_token(device_code)

        if 'error' not in data:
            access_token = data.get('access_token', '')
            refresh_token = data.get('refresh_token', '')
            token_expiry = time.time() + int(data.get('expires_in', 3600))

            if not access_token and not refresh_token:
                token_expiry = -1

            USERS.access_token = access_token
            USERS.refresh_token = refresh_token
            USERS.token_expiry = token_expiry
            USERS.save()
            self.refresh_client()
            return True

        if data['error'] == 'authorization_pending':
            return False

        return data

    def refresh_client(self):
        USERS.load()
        self._api.ACCESS_TOKEN = USERS.access_token
        self.client = oauth.Client()
        memoizer.reset_cache()
        DataCache().clear()

    def calculate_next_page_token(self, page):
        """
            Copyright (C) 2014-2016 bromix (plugin.video.youtube)
            Copyright (C) 2016-2020 plugin.video.youtube
            SPDX-License-Identifier: GPL-2.0-only
            See LICENSES/GPL-2.0-only for more information.
        """
        low = 'AEIMQUYcgkosw048'
        high = 'ABCDEFGHIJKLMNOP'

        position = (page - 1) * self.max_results

        overflow_token = 'Q'
        if position >= 128:
            overflow_token_iteration = position // 128
            overflow_token = '%sE' % high[overflow_token_iteration]

        low_iteration = position % len(low)

        if position >= 256:
            multiplier = (position // 128) - 1
            position -= 128 * multiplier

        high_iteration = (position // len(low)) % len(high)

        return 'C%sAA' % ''.join([high[high_iteration], low[low_iteration], overflow_token])
