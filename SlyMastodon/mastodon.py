'''
Mastodon API client and authenticated types

https://docs.joinmastodon.org/api/
'''
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
import re
from typing import IO, cast, overload
from SlyAPI import *
from SlyAPI.web import Method, ApiError
from aiohttp import FormData

from .entities import *
from .public import MastodonPublic

# like @username@domain
RE_AT_AT = re.compile(r'@(\w+)@(\w+)')
# like @username
RE_AT = re.compile(r'@(\w+)')

class ScopeSimple:
    '''
    Top level scopes for OAuth2

    https://docs.joinmastodon.org/api/oauth-scopes/
    '''
    READ = "read"
    WRITE = "write"
    FOLLOW = "follow"
    PUSH = "push"

class ScopeGranular:
    '''
    Granular scopes for OAuth2

    https://docs.joinmastodon.org/api/oauth-scopes/
    '''
    READ_ACCOUNTS = "read:accounts"
    READ_BLOCKS = "read:blocks"
    READ_BOOKMARKS = "read:bookmarks"
    READ_FAVOURITES = "read:favourites"
    READ_FILTERS = "read:filters"
    READ_FOLLOWS = "read:follows"
    READ_LISTS = "read:lists"
    READ_MUTES = "read:mutes"
    READ_NOTIFICATIONS = "read:notifications"
    READ_SEARCH = "read:search"
    READ_STATUSES = "read:statuses"

    WRITE_ACCOUNTS = "write:accounts"
    WRITE_BLOCKS = "write:blocks"
    WRITE_BOOKMARKS = "write:bookmarks"
    WRITE_CONVERSATIONS = "write:conversations"
    WRITE_FAVOURITES = "write:favourites"
    WRITE_FILTERS = "write:filters"
    WRITE_FOLLOWS = "write:follows"
    WRITE_LISTS = "write:lists"
    WRITE_MEDIA = "write:media"
    WRITE_MUTES = "write:mutes"
    WRITE_NOTIFICATIONS = "write:notifications"
    WRITE_REPORTS = "write:reports"
    WRITE_STATUSES = "write:statuses"

@dataclass
class CredentialSource(DataclassJsonMixin):
    '''Extra info provided for the account of an authorized user'''
    sensitive: bool
    language: str
    note: str
    privacy: PrivacyDirect
    fields: list[UserField]
    follow_requests_count: int

class AuthorizedUser(User):
    '''
    The currently authenticated user

    https://docs.joinmastodon.org/entities/Account/#CredentialAccount
    '''
    source: CredentialSource
    role: Role

class AuthorizedPost(Post):
    '''
    A post made by the authorized user with some extra fields
    
    https://docs.joinmastodon.org/entities/Status/#favourited
    '''
    favourited: bool
    reblogged: bool
    muted: bool
    bookmarked: bool
    pinned: bool
    filtered: bool
    
@dataclass
class PollSetup:
    '''Parameters for creating a poll when posting'''
    options: list[str]
    expires_in: int # seconds
    multiple: bool|None
    hide_totals: bool|None

@dataclass
class ScheduledPostParams(DataclassJsonMixin):
    '''https://docs.joinmastodon.org/entities/ScheduledStatus/#params'''
    text: str
    poll: PollSetup|None
    media_ids: list[str]|None
    sensitive: bool|None
    spoiler_text: str|None
    visibility: PrivacyDirect
    in_reply_to_id: str|None
    language: str|None
    application_id: str|None
    idempotency: str|None
    with_rate_limit: bool

@dataclass
class ScheduledPost(DataclassJsonMixin):
    '''
    A scheduled post that has not been posted yet
    
    https://docs.joinmastodon.org/entities/ScheduledStatus/
    '''
    id: str
    scheduled_at: datetime
    params: ScheduledPostParams
    media_attachments: list[MediaAttachment]

import urllib3
import os
import aiofiles
import aiofiles.os
import mimetypes

def _check_size(size: int|float, max_bytes: int|None=None) -> None:
    if max_bytes and size > max_bytes:
        raise ValueError(F"File too large: {size} > {max_bytes}")

def _mime_type(filename: str) -> str:
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"

def _media_ids(media: list[str|MediaAttachment]|None) -> list[str]|None:
    if media is None: return None
    return [ str(m) for m in media ]

class Mastodon(MastodonPublic):
    '''
    Mastodon API client
    '''
    # ISO 639 language code
    lang: str

    def __init__(self, instance_url: str, auth: OAuth2, lang: str = "en"):
        super().__init__(instance_url, auth)
        self.lang = lang

    async def _load_or_download_file(self, file: str|tuple[str, IO[bytes]|bytes], max_bytes: int|None=None) -> tuple[str, bytes]:
        match file:
            case str(path) if os.path.isfile(path):
                filename = os.path.basename(path)
                size = (await aiofiles.os.stat(path)).st_size
                _check_size(size, max_bytes)
                async with aiofiles.open(path, "rb") as f:
                    return filename, await f.read()
            case str(url) if path := urllib3.util.parse_url(url).path:
                filename = os.path.basename(path)
                async with self._client.get(url) as r:
                    if r.status != 200:
                        raise ValueError(F"Failed to download file: {r.status}")
                    elif max_bytes:
                        _check_size(r.content_length or float('inf'), max_bytes)
                    return filename, await r.read()
            case str(other):
                raise ValueError(F"File not found: {other}")
            case (filename, bytes(b)):
                _check_size(len(b), max_bytes)
                return filename, b
            case (filename, io):
                io = cast(IO[bytes], io)
                if max_bytes:
                    io.seek(0, 2)
                    _check_size(io.tell(), max_bytes)
                    io.seek(0)
                return filename, io.read()

    def set_default_lanuage(self, lang: str):
        '''
        Set the default language used to annotate posts with
        ISO 639
        ex. "en", "ja", "zh", "fr"
        '''
        self.lang = lang

    @requires_scopes(ScopeGranular.READ_ACCOUNTS)
    async def me(self) -> AuthorizedUser:
        '''Get the currently authenticated user'''
        return await self._get(AuthorizedUser, "v1/accounts/verify_credentials")
    
    @overload
    async def _statuses_post(self, text: str|None = None, media: list[str|MediaAttachment]|None = None, reply_to: str|None = None, poll: PollSetup|None = None, sensitive: bool|None = None, spoiler_text: str|None = None, privacy: Privacy|None = None, scheduled_at: None = None, lang: str|None = None) -> Post: ...

    @overload
    async def _statuses_post(self, text: str|None, media: list[str|MediaAttachment]|None, reply_to: str|None, poll: PollSetup|None, sensitive: bool|None, spoiler_text: str|None, privacy: Privacy|None, scheduled_at: datetime, lang: str|None) -> ScheduledPost: ...
    
    async def _statuses_post(self, text: str|None = None, media: list[str|MediaAttachment]|None = None, reply_to: str|None = None, poll: PollSetup|None = None, sensitive: bool|None = None, spoiler_text: str|None = None, privacy: Privacy|None = None, scheduled_at: datetime|None = None, lang: str|None = None) -> Post|ScheduledPost:
        data = {}
        if text: data["status"] = text
        if media: data['media_ids'] = _media_ids(media)
        if reply_to: data['in_reply_to_id'] = reply_to
        if poll: data['poll'] = asdict(poll)
        if sensitive: data['sensitive'] = sensitive
        if spoiler_text: data['spoiler_text'] = spoiler_text
        if privacy: data['visibility'] = privacy.value
        if lang: data['language'] = lang
        if scheduled_at: data['scheduled_at'] = scheduled_at.isoformat()
        kind = ScheduledPost if scheduled_at is None else Post
        return await self._post(kind, "v1/statuses", data=data)
    
    @requires_scopes(ScopeGranular.WRITE_STATUSES)
    async def post(self, text: str, 
                   media: list[str|MediaAttachment]|None = None, 
                   reply_to: str|None = None, 
                   sensitive: bool = False,
                   spoiler_text: str|None = None,
                   privacy: Privacy = Privacy.PUBLIC,
                   lang: str|None = None) -> Post:
        '''Make a new post'''
        return await self._statuses_post(text, media, reply_to, sensitive=sensitive, spoiler_text=spoiler_text, privacy=privacy, lang=lang)
    
    async def post_media(self,
                         media: list[str|MediaAttachment],
                         reply_to: str|None = None,
                         sensitive: bool = False,
                         spoiler_text: str|None = None,
                         privacy: Privacy = Privacy.PUBLIC,
                         lang: str|None = None) -> Post:
        '''Make a new post with no text and only images'''
        return await self._statuses_post(None, media, reply_to, sensitive=sensitive, spoiler_text=spoiler_text, privacy=privacy, lang=lang)
    
    async def post_poll(self, text: str, 
                        poll: PollSetup, 
                        reply_to: str|None = None, 
                        sensitive: bool = False, 
                        spoiler_text: str|None = None, 
                        privacy: Privacy = Privacy.PUBLIC, 
                        lang: str|None = None) -> Post:
        '''Make a new post with a poll'''
        return await self._statuses_post(text, None, reply_to, poll, sensitive=sensitive, spoiler_text=spoiler_text, privacy=privacy, lang=lang)

    
    async def edit_post(self, post_id: str, text: str, 
                        media: list[str|MediaAttachment]|None = None, 
                        reply_to: str|None = None, 
                        poll: PollSetup|None = None, 
                        sensitive: bool = False, 
                        spoiler_text: str|None = None, 
                        privacy: Privacy = Privacy.PUBLIC, 
                        scheduled_at: datetime|None = None, 
                        lang: str|None = None) -> Post:
        '''Replace an existing post'''
        data = {}
        if text: data["status"] = text
        if media: data['media_ids'] = _media_ids(media)
        if reply_to: data['in_reply_to_id'] = reply_to
        if poll: data['poll'] = poll
        if sensitive: data['sensitive'] = sensitive
        if spoiler_text: data['spoiler_text'] = spoiler_text
        if privacy: data['visibility'] = privacy.value
        if lang: data['language'] = lang
        if scheduled_at: data['scheduled_at'] = scheduled_at.isoformat()
        return await self._put(Post, F"v1/statuses/{post_id}", data=data)
    
    async def get_my_post(self, post_id: str) -> AuthorizedPost:
        '''Get a post with extra info, if posted by the authorized user, by ID'''
        return await self._get(AuthorizedPost, F"v1/statuses/{post_id}")
    
    async def delete_post(self, post_id: str) -> DeletedPost:
        '''Delete a post by ID'''
        return await self._delete(DeletedPost, F"v1/statuses/{post_id}")
    
    async def boost(self, post_id: str, privacy: Privacy = Privacy.PUBLIC):
        '''Boost a post'''
        data = { "visibility": privacy.value }
        await self._post(None, F"v1/statuses/{post_id}/reblog", data=data)

    async def schedule_post(self, text: str, scheduled_at: datetime, media: list[str|MediaAttachment]|None = None, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, privacy: Privacy = Privacy.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post, at least 5 minutes in the future'''
        return await self._statuses_post(text, media, reply_to, None, sensitive, spoiler_text, privacy, scheduled_at, lang)
    
    async def schedule_media(self, media: list[str|MediaAttachment], scheduled_at: datetime, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, privacy: Privacy = Privacy.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post with no text and only images, at least 5 minutes in the future'''
        return await self._statuses_post(None, media, reply_to, None, sensitive, spoiler_text, privacy, scheduled_at, lang)
    
    async def schedule_poll(self, text: str, poll: PollSetup, scheduled_at: datetime, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, privacy: Privacy = Privacy.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post with a poll, at least 5 minutes in the future'''
        return await self._statuses_post(text, None, reply_to, poll, sensitive, spoiler_text, privacy, scheduled_at, lang)
    
    async def _start_media_upload(self, file: str|tuple[str, bytes|IO[bytes]], thumbnail: str|tuple[str, bytes|IO[bytes]]|None=None, description: str|None=None, focus: tuple[float, float]|None=None) -> MediaAttachment|UnuploadedMediaAttachment:
        data = FormData()
        filename, content = await self._load_or_download_file(file)
        data.add_field('file', content, filename=filename, content_type=_mime_type(filename))
        if description:
            data.add_field('description', description)
        if thumbnail:
            filename, content = await self._load_or_download_file(thumbnail)
            data.add_field('thumbnail', content, filename=filename, content_type=_mime_type(filename))
        if focus:
            x, y = focus
            if max(abs(x), abs(y)) > 1:
                raise ValueError("Focus must be a tuple of floats between -1 and 1")
            data.add_field('focus', F"{x},{y}")

        async with await self._request_context(Method.POST, "v2/media", data=data) as r:
            if r.status == 200:
                return MediaAttachment.from_json(await r.json())
            elif r.status == 202:
                return UnuploadedMediaAttachment.from_json(await r.json())
            elif r.status == 422:
                raise ValueError("Invalid media file")
            else:
                raise await ApiError.from_resposnse(r)

    async def _check_media_upload(self, media_id: str) -> MediaAttachment|None:
        async with await self._request_context(Method.GET, F"media/{media_id}") as r:
            if r.status == 200:
                return MediaAttachment.from_json(await r.json())
            elif r.status == 206:
                return None
            else:
                raise await ApiError.from_resposnse(r)
            
    async def media(self, media_id: str) -> MediaAttachment:
        '''Get information about a media file'''
        while (media :=
               await self._check_media_upload(media_id)) is None:
            # wait for the media to finish uploading
            await asyncio.sleep(1)
        return media
            
    async def upload(self, file: str|tuple[str, bytes|IO[bytes]], thumbnail: str|tuple[str, bytes|IO[bytes]]|None=None, description: str|None=None, focus: tuple[float, float]|None=None) -> MediaAttachment:
        '''Upload a file to the server'''
        media = await self._start_media_upload(file, thumbnail, description, focus)
        if isinstance(media, UnuploadedMediaAttachment):
            media = await self.media(media.id)
        return media
    
    async def update_media(self, media: str|MediaAttachment|UnuploadedMediaAttachment, thumbnail: str|tuple[str, bytes|IO[bytes]]|None=None, description: str|None=None, focus: tuple[float, float]|None=None):
        data = FormData()
        media_id = media if isinstance(media, str) else media.id
        if not any((thumbnail, description, focus)):
            raise ValueError("Provide at least one of thumbnail, description, or focus")
        if description:
            data.add_field('description', description)
        if thumbnail:
            filename, content = await self._load_or_download_file(thumbnail)
            data.add_field('thumbnail', content, filename=filename, content_type=_mime_type(filename))
        if focus:
            x, y = focus
            if max(abs(x), abs(y)) > 1:
                raise ValueError("Focus must be a tuple of floats between -1 and 1")
            data.add_field('focus', F"{x},{y}")
        await self._put(None, F"media/{media_id}", data=data)

