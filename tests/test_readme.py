from SlyMastodon import *

async def test_readme():
    m = Mastodon( "mastodon.skye.vg",
                  OAuth2("tests/app.json", "tests/user.json") )
    
    user = await m.me()

    print(user.at_username) # @dunkyl@skye.vg
