from SlyMastodon import *

async def test_readme():
    m = Mastodon( "https://mastodon.social",
                  OAuth2("app.json", "user.json") )
    
    user = await m.me()

    print(user.at_username)
