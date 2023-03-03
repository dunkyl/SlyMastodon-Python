import sys, asyncio, pytest
from SlyMastodon import *

auth = OAuth2("tests/app.json", "tests/user.json")

@pytest.mark.skipif(sys.gettrace() is None, reason="Posts real.")
async def test_toot():

    mast = Mastodon("mastodon.skye.vg", auth)

    toot = await mast.post("test post please ignore")

    toot_get = await mast.get_post(toot.id)

    toot_get_mine = await mast.get_my_post(toot.id)

    assert toot.content == toot_get.content == toot_get_mine.content

    await asyncio.sleep(1)

    _deleted = await mast.delete_post(toot.id)

