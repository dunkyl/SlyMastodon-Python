from SlyAPI import *
from SlyAPI.auth import NoAuth

from .entities import *

class MastodonPublic(WebAPI):
    '''
    Mastodon client for public API
    '''

    def __init__(self, instance_url: str, auth: OAuth2|None = None):
        super().__init__(auth or NoAuth(), True)
        if not instance_url.startswith('https://'):
            instance_url = F"https://{instance_url}"
        self.base_url = instance_url + "/api/"

    async def user(self, at_or_id: str) -> User:
        '''
        Lookup an account by ID or username
        @user : defaults to the current domain
        @user@domain : any other domain
        '''
        if at_or_id.startswith("@"):
            return await self._get(User, "v1/accounts/lookup", {"acct": at_or_id[1:]} )
        else: # ID
            return await self._get(User, F"v1/accounts/{at_or_id}")
    
    async def get_post(self, post_id: str) -> Post:
        '''Get a post by ID'''
        return await self._get(Post, F"v1/statuses/{post_id}")