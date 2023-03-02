# SlyMastodon for Python

> 🚧 **Work in progress**

> 🐍 For Python 3.11+

No-boilerplate, *async* and *typed* Mastodon access! 😋
```sh
pip install slymastodon
```
This library does not proivde full coverage. Currently, only the following topics are supported:
- Getting the current user and other users
- Posting, scheduling, retrieving, and deleting toots

---

## Example Usage

```python
import asyncio
from SlyMastodon import *

async def main():
    m = Mastodon( "https://mastodon.social",
                  OAuth2("app.json", "user.json") )
    
    user = await m.me()

asyncio.run(main())
```

---

## Example CLI Usage

```sh
py -m SlyMastodon scaffold
# ...
py -m SlyMastodon grant
```