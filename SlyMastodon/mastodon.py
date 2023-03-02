'''
Mastodon API and types
https://docs.joinmastodon.org/api/
'''
from dataclasses import dataclass
import datetime
from enum import Enum
import re
from typing import Any
from SlyAPI import *

# like @username@domain
RE_AT_AT = re.compile(r'@([a-zA-Z0-9_]+)@([a-zA-Z0-9_]+)')
# like @username
RE_AT = re.compile(r'@([a-zA-Z0-9_]+)')


class ScopeSimple:
    READ = "read"
    WRITE = "write"
    FOLLOW = "follow"
    PUSH = "push"

class ScopeGranular:
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

class V8y(Enum):
    '''Visibility'''
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

Visibility = V8y

class V8yEx(Enum):
    '''Extended visibility for direct messages'''
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    DIRECT = "direct"
    LIMITED = "limited"

VisibilityEx = V8yEx

class Emoji: pass

class UserField: pass

class User:
    id: str
    username: str
    # acct: str
    display_name: str
    locked: bool
    bot: bool
    created_at: datetime.datetime
    discoverable: bool
    note: str
    url: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    followers_count: int
    following_count: int
    statuses_count: int
    last_status_at: datetime.datetime
    emojis: list[Emoji]
    fields: list[UserField]

    # TODO: how
    domain: str
    at_username: str # @username@domain

    def __init__(self, src: Any):
        raise NotImplementedError()
    
def clean_html(html: str) -> str:
    raise NotImplementedError()

class Post:
    '''A post, toot, tweet, or status'''
    id: str
    created_at: datetime.datetime
    # ...
    html_content: str
    # ...

    @property
    def content(self) -> str:
        return clean_html(self.html_content)

    def __init__(self, src: Any):
        raise NotImplementedError()
    
class ScheduledPost:
    '''A scheduled post that has not been posted yet'''
    scheduled_at: datetime.datetime
    params: dict[str, Any]

    def __init__(self, src: Any):
        raise NotImplementedError()
    
@dataclass
class Poll:
    options: list[str]
    expires_in: int # seconds
    multiple: bool
    hide_totals: bool

# class CredentialAccount(User):
#     source: Any

class Mastodon(WebAPI):
    '''
    Mastodon API client
    '''

    def __init__(self, instance_url: str, auth: OAuth2, lang: str = "en"):
        super().__init__(auth)
        self.base_url = instance_url + "/api/v1/"
        self.lang = lang

    def set_default_lanuage(self, lang: str):
        '''
        Set the default language used to annotate posts with
        ISO 639
        ex. "en", "ja", "zh", "fr"
        '''
        self.lang = lang

    async def account(self, account: str) -> User:
        '''
        Lookup an account by ID or username
        @user : defaults to the current domain
        @user@domain : any other domain
        '''
        if account.startswith("@"):
            return User(
                await self.get_json(F"accounts/lookup", {"acct": account[1:]})
            )
        else: # ID
            return User(
                await self.get_json(F"accounts/{account}")
            )

    @requires_scopes(ScopeGranular.READ_ACCOUNTS)
    async def me(self):
        '''Get the currently authenticated user'''
        return await self.account("verify_credentials")
    
    async def post(self, text: str, media_ids: list[str]|None = None, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC,lang: str|None = None) -> Post:
        '''Make a new post'''
        data = {
            "status": text,
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
            'in_reply_to_id': reply_to
        }
        return Post(await self.post_form(F"statuses", data))
    
    async def post_media(self, media_ids: list[str], reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC,lang: str|None = None) -> Post:
        '''Make a new post with no text and only images'''
        data = {
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
            'in_reply_to_id': reply_to
        }
        return Post(await self.post_form(F"statuses", data))
    
    async def post_poll(self, text: str, poll: Poll, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC,lang: str|None = None) -> Post:
        '''Make a new post with a poll'''
        data = {
            "status": text,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
            'in_reply_to_id': reply_to,
            # TODO: is it really like this or should it be a nested dict?
            'poll[options]': poll.options,
            'poll[expires_in]': poll.expires_in,
            'poll[multiple]': poll.multiple,
            'poll[hide_totals]': poll.hide_totals
        }
        return Post(await self.post_form(F"statuses", data))

    
    async def edit_post(self, post_id: str, text: str, media_ids: list[str]|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC, lang: str|None = None) -> Post:
        '''Edit an existing post'''
        data = {
            "status": text,
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
        }
        return Post(await self.put_form(F"statuses/{post_id}", data))
    
    
    async def get_post(self, post_id: str) -> Post:
        '''Get a post by ID'''
        return Post(await self.get_json(F"statuses/{post_id}"))
    
    async def delete_post(self, post_id: str):
        '''Delete a post by ID'''
        await self.delete_json(F"statuses/{post_id}")
    
    async def boost(self, post_id: str, visibility: V8y = V8y.PUBLIC):
        '''Boost a post'''
        data = { "visibility": visibility }
        await self.post_form(F"statuses/{post_id}/reblog", data=data)

    async def schedule_post(self, text: str, scheduled_at: datetime.datetime, media_ids: list[str]|None = None, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post, at least 5 minutes in the future'''
        data = {
            "status": text,
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
            'in_reply_to_id': reply_to,
            'scheduled_at': scheduled_at.isoformat()
        }
        return ScheduledPost(await self.post_form(F"statuses", data))
    
    async def schedule_media(self, media_ids: list[str], scheduled_at: datetime.datetime, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post with no text and only images, at least 5 minutes in the future'''
        data = {
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
            'in_reply_to_id': reply_to,
            'scheduled_at': scheduled_at.isoformat()
        }
        return ScheduledPost(await self.post_form(F"statuses", data))
    
    async def schedule_poll(self, text: str, poll: Poll, scheduled_at: datetime.datetime, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: V8y = V8y.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post with a poll, at least 5 minutes in the future'''
        data = {
            "status": text,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility,
            'in_reply_to_id': reply_to,
            'scheduled_at': scheduled_at.isoformat(),
        }
        return ScheduledPost(await self.post_form(F"statuses", data))
