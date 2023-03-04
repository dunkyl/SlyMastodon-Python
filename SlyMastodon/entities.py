'''
Mastodon public API types
'''
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from SlyAPI import *
from SlyAPI.web import JsonMap

from .serialization import DataclassJsonMixin

class Privacy(Enum):
    '''Visibility'''
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"

class PrivacyDirect(Enum):
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
    privacy: PrivacyDirect
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
class _MediaAttachmentBase(DataclassJsonMixin):
    id: str
    type: MediaType
    preview_url: str
    remote_url: str|None
    meta: JsonMap
    description: str
    blurhash: str

class MediaAttachment(_MediaAttachmentBase):
    url: str

    def str(self) -> str:
        return self.id

class UnuploadedMediaAttachment(_MediaAttachmentBase):
    url: str|None

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
    visibility: PrivacyDirect
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
    visibility: PrivacyDirect
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