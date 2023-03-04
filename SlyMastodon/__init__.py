'''
Mastodon client library
'''
from .mastodon import Mastodon as Mastodon, OAuth2 as OAuth2
from .public import MastodonPublic as MastodonPublic
from .entities import PollSetup as PollSetup, Privacy as Privacy, \
    Post as Post, User as User
