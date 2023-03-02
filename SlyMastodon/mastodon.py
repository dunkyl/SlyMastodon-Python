'''
Mastodon API and types
https://docs.joinmastodon.org/api/
'''
from SlyAPI import *

class Mastodon(WebAPI):

    def __init__(self, instance_url: str, auth: OAuth2):
        super().__init__(auth)
        self.base_url = instance_url

    async def me(self):
        raise NotImplementedError()