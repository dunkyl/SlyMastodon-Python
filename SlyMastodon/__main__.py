import sys, asyncio, inspect

from SlyMastodon.mastodon import ScopeSimple
from SlyAPI.flow import *

async def main(args: list[str]):

    match args:
        case ['grant']:
            await grant_wizard(ScopeSimple, kind='OAuth2')
        case ['scaffold', instance_url]:
            if not instance_url.startswith('https://'):
                instance_url = F"https://{instance_url}"
            scaffold_wizard(kind='OAuth2', override={
                "token_uri": F"{instance_url}/oauth/token",
                "auth_uri": F"{instance_url}/oauth/authorize"
            })
        case _: # help
            print(inspect.cleandoc("""
            SlyMastodon command line: tool for Mastodon OAuth2.
            Usage:
                SlyMastodon scaffold instance_url
                    Template an OAuth2 client credentials file for an instance.
                SlyMastodon grant
                    Grant an OAuth2 access token.
            """))

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))