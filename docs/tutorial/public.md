# Public Mastodon API

Most of the read-only Mastodon API is public and does not require authentication. This means that you can use it to get information about users, statuses, and other things without having to log in. This is useful for things like bots that don't need to post or follow people.

## Public-only API client

SlyMastodon has a public-only API client, [`MastodonPublic`](SlyMastodon.public.MastodonPublic), which can be used to access the public API. 

```py
from SlyMastodon import MastodonPublic

async def main():
    mast = MastodonPublic("mastodon.skye.vg")

    dunkyl = await mast.account("@dunkyl")

    print(dunkyl.display_name) # Dunkyl 🔣🔣
asyncio.run(main())
```

An authenticated [`Mastodon`](SlyMastodon.mastodon.Mastodon) client can also be used to access any of the methods for the public API.