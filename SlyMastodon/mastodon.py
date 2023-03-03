'''
Mastodon API and types
https://docs.joinmastodon.org/api/
'''
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
from SlyAPI import *
from SlyAPI.web import JsonMap

from .serialization import DataclassJsonMixin

# like @username@domain
RE_AT_AT = re.compile(r'@(\w+)@(\w+)')
# like @username
RE_AT = re.compile(r'@(\w+)')

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

class Visibility(Enum):
    '''Visibility'''
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

class VisibilityDirect(Enum):
    '''Extended visibility for direct messages'''
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    DIRECT = "direct"
    # LIMITED = "limited"

class MediaType(Enum):
    '''Media type'''
    IMAGE = "image"
    GIFV = "gifv"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"

@dataclass
class Emoji:
    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool
    category: str

@dataclass
class UserField(DataclassJsonMixin):
    name: str
    value: str
    verified_at: datetime

@dataclass
class User(DataclassJsonMixin):
    id: str
    username: str
    acct: str
    display_name: str
    locked: bool
    bot: bool
    created_at: datetime
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
    last_status_at: datetime
    emojis: list[Emoji]
    fields: list[UserField]

    @property
    def at_username(self) -> str:
        '''Full webfinger address'''
        domain = self.url.split('/')[2]
        domain = '.'.join(domain.split('.')[-2:])
        return f"@{self.username}@{domain}"

@dataclass
class Role:
    id: str
    name: str
    dolor: str
    position: int
    permissions: int
    highlighted: bool
    created_at: str
    updated_at: str

@dataclass
class CredentialSource(DataclassJsonMixin):
    privacy: VisibilityDirect
    sensitive: bool
    language: str
    note: str
    visibility: str
    fields: list[UserField]
    follow_requests_count: int

class AuthorizedUser(User):
    source: CredentialSource
    role: Role
    
@dataclass
class MediaAttachment(DataclassJsonMixin):
    id: str
    type: MediaType
    url: str
    preview_url: str
    remote_url: str|None
    meta: JsonMap
    description: str
    blurhash: str

@dataclass
class Application:
    name: str
    website: str|None

@dataclass
class StatusMention:
    id: str
    username: str
    url: str
    acct: str

@dataclass
class StatusTag:
    name: str
    url: str

@dataclass
class PollOption:
    title: str
    votes_count: int

@dataclass
class Poll(DataclassJsonMixin):
    id: str
    expires_at: datetime
    expired: bool
    multiple: bool
    votes_count: int
    options: list[PollOption]
    voted: bool|None
    own_votes: list[int]|None

class PreviewType(Enum):
    '''Preview type'''
    LINK = "link"
    PHOTO = "photo"
    VIDEO = "video"
    RICH = "rich"

@dataclass
class PreviewCard(DataclassJsonMixin):
    url: str
    title: str
    description: str
    type: PreviewType
    author_name: str
    author_url: str
    provider_name: str
    provider_url: str
    height: int
    image: str|None
    embed_url: str
    blurhash: str|None

@dataclass
class _PostBase(DataclassJsonMixin):
    id: str
    created_at: str
    account: User
    visibility: VisibilityDirect
    sensitive: bool
    spoiler_text: str
    media_attachments: list[MediaAttachment]
    application: Application|None
    mentions: list[StatusMention]
    tags: list[StatusTag]
    emojis: list[Emoji]
    reblogs_count: int
    favourites_count: int
    replies_count: int
    url: str|None
    in_reply_to_id: str|None
    in_reply_to_account_id: str|None
    reblog: 'Post|None'
    poll: Poll|None
    card: PreviewCard|None
    language: str|None
    edited_at: str|None

class Post(_PostBase):
    '''A post, toot, tweet, or status'''
    content: str

class DeletedPost(_PostBase):
    '''A deleted post'''
    text: str|None

class AuthorizedPost(Post):
    favourited: bool
    reblogged: bool
    muted: bool
    bookmarked: bool
    pinned: bool
    filtered: bool
    
@dataclass
class PollSetup:
    options: list[str]
    expires_in: int # seconds
    multiple: bool|None
    hide_totals: bool|None

@dataclass
class ScheduledPostParams(DataclassJsonMixin):
    text: str
    poll: PollSetup|None
    media_ids: list[str]|None
    sensitive: bool|None
    spoiler_text: str|None
    visibility: VisibilityDirect
    in_reply_to_id: str|None
    language: str|None
    application_id: str|None
    idempotency: str|None
    with_rate_limit: bool

@dataclass
class ScheduledPost(DataclassJsonMixin):
    '''A scheduled post that has not been posted yet'''
    id: str
    scheduled_at: datetime
    params: ScheduledPostParams
    media_attachments: list[MediaAttachment]

class Mastodon(WebAPI):
    '''
    Mastodon API client
    '''

    def __init__(self, instance_url: str, auth: OAuth2, lang: str = "en"):
        super().__init__(auth, True)
        if not instance_url.startswith('https://'):
            instance_url = F"https://{instance_url}"
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
            return await self._get(User, "accounts/lookup", {"acct": account[1:]} )
        else: # ID
            return await self._get(User, F"accounts/{account}")

    @requires_scopes(ScopeGranular.READ_ACCOUNTS)
    async def me(self) -> AuthorizedUser:
        '''Get the currently authenticated user'''
        return await self._get(AuthorizedUser, "accounts/verify_credentials")
    
    async def _statuses_post(self, text: str|None = None, media_ids: list[str]|None = None, reply_to: str|None = None, poll: PollSetup|None = None, sensitive: bool|None = None, spoiler_text: str|None = None, visibility: Visibility|None = None, lang: str|None = None) -> Post:
        data = {}
        if text: data["status"] = text
        if media_ids: data['media_ids'] = media_ids
        if reply_to: data['in_reply_to_id'] = reply_to
        if poll: data['poll'] = poll
        if sensitive: data['sensitive'] = sensitive
        if spoiler_text: data['spoiler_text'] = spoiler_text
        if visibility: data['visibility'] = visibility.value
        if lang: data['language'] = lang
        return await self._post(Post, "statuses", data=data)
    
    @requires_scopes(ScopeGranular.WRITE_STATUSES)
    async def post(self, text: str, media_ids: list[str]|None = None, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC,lang: str|None = None) -> Post:
        '''Make a new post'''
        return await self._statuses_post(text, media_ids, reply_to, sensitive=sensitive, spoiler_text=spoiler_text, visibility=visibility, lang=lang)
    
    async def post_media(self, media_ids: list[str], reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC,lang: str|None = None) -> Post:
        '''Make a new post with no text and only images'''
        return await self._statuses_post(None, media_ids, reply_to, sensitive=sensitive, spoiler_text=spoiler_text, visibility=visibility, lang=lang)
    
    async def post_poll(self, text: str, poll: PollSetup, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC, lang: str|None = None) -> Post:
        '''Make a new post with a poll'''
        return await self._statuses_post(text, None, reply_to, poll, sensitive=sensitive, spoiler_text=spoiler_text, visibility=visibility, lang=lang)

    
    async def edit_post(self, post_id: str, text: str, media_ids: list[str]|None = None, reply_to: str|None = None, poll: PollSetup|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC, lang: str|None = None) -> Post:
        '''Edit an existing post'''
        data = {}
        if text: data["status"] = text
        if media_ids: data['media_ids'] = media_ids
        if reply_to: data['in_reply_to_id'] = reply_to
        if poll: data['poll'] = poll
        if sensitive: data['sensitive'] = sensitive
        if spoiler_text: data['spoiler_text'] = spoiler_text
        if visibility: data['visibility'] = visibility.value
        if lang: data['language'] = lang
        return await self._put(Post, F"statuses/{post_id}", data=data)
    
    async def get_post(self, post_id: str) -> Post:
        '''Get a post by ID'''
        return await self._get(Post, F"statuses/{post_id}")
    
    async def get_my_post(self, post_id: str) -> AuthorizedPost:
        '''Get a post with extra info, if posted by the authorized user, by ID'''
        return await self._get(AuthorizedPost, F"statuses/{post_id}")
    
    async def delete_post(self, post_id: str) -> DeletedPost:
        '''Delete a post by ID'''
        return await self._delete(DeletedPost, F"statuses/{post_id}")
    
    async def boost(self, post_id: str, visibility: Visibility = Visibility.PUBLIC):
        '''Boost a post'''
        data = { "visibility": visibility.value }
        await self._post(None, F"statuses/{post_id}/reblog", data=data)

    async def schedule_post(self, text: str, scheduled_at: datetime, media_ids: list[str]|None = None, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post, at least 5 minutes in the future'''
        data = {
            "status": text,
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility.value,
            'in_reply_to_id': reply_to,
            'scheduled_at': scheduled_at.isoformat()
        }
        return await self._post(ScheduledPost, "statuses", data=data)
    
    async def schedule_media(self, media_ids: list[str], scheduled_at: datetime, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post with no text and only images, at least 5 minutes in the future'''
        data = {
            'media_ids': media_ids,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility.value,
            'in_reply_to_id': reply_to,
            'scheduled_at': scheduled_at.isoformat()
        }
        return await self._post(ScheduledPost, "statuses", data=data)
    
    async def schedule_poll(self, text: str, poll: PollSetup, scheduled_at: datetime, reply_to: str|None = None, sensitive: bool = False, spoiler_text: str|None = None, visibility: Visibility = Visibility.PUBLIC,lang: str|None = None) -> ScheduledPost:
        '''Schedule a new post with a poll, at least 5 minutes in the future'''
        data = {
            "status": text,
            'language': lang or self.lang,
            'sensitive': sensitive,
            'spoiler_text': spoiler_text,
            'visibility': visibility.value,
            'in_reply_to_id': reply_to,
            'scheduled_at': scheduled_at.isoformat(),
        }
        return await self._post(ScheduledPost, "statuses", data=data)
