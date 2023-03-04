'''
Mastodon client library
'''
from .mastodon import Mastodon as Mastodon, OAuth2 as OAuth2, \
    PollSetup as PollSetup
from .public import MastodonPublic as MastodonPublic
from .entities import Privacy as Privacy, Post as Post, User as User
