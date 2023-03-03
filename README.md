# SlyMastodon for Python

> **Warning**
>
> This package is an early work in progress. Breaking changes may be frequent!

> 🐍 For Python 3.11+

No-boilerplate, *async* and *typed* Mastodon access! 😋
```sh
pip install slymastodon
```
This library does not proivde full coverage. Currently, only the following topics are supported:
- Getting the current user and other users
- Submitting, scheduling, retrieving, and deleting post

---

## Example Usage

```python
import asyncio
from SlyMastodon import *

async def main():
    m = Mastodon( "mastodon.skye.vg",
                  OAuth2("app.json", "user.json") )
    
    user = await m.me()

    print(user.at_username) # @dunkyl@skye.vg

asyncio.run(main())
```

---

## Example CLI Usage

```sh
py -m SlyMastodon scaffold
# ...
py -m SlyMastodon grant
```
