# Getting Started

## Installation

SlyMastodon is available on PyPI, as long as you have [Python newer than 3.11](https://python.org). You can install it with `pip`:

```sh
pip install slymastodon
```

## Before you begin

Before you begin, you should have a Mastodon account. If you do not, you can create one [here](https://joinmastodon.org/). You will also need to know the URL of the instance you want to use. For the purposes of this tutorial, we will use `mastodon.skye.vg` as the instance URL, since that is the instance I use.

Note that you will need to replace `mastodon.skye.vg` with the URL of the instance you want to use in the following examples.

SlyMastodon also is not a framework or a library aiming to be as accessible as possible. If you aren't familiar with Python, you might want to learn the basics first. If you are familiar with Python, you might want to learn about [asyncio](https://docs.python.org/3/library/asyncio.html) and [type hints](https://docs.python.org/3/library/typing.html) before you begin, as they are used extensively in SlyMastodon and a key part of its design and purpose.

## Public or Authenticated?

In order to control an account, either as a bot or on behalf of a user, you will need to authenticate with the instance. Continue below for instructions on how to do this.

If you only need to read some kinds of data from the instance, you can use the [public API](public.md), which does not require authentication.

## Getting credentials

SlyMastodon uses OAuth2 to authenticate with Mastodon, which means that you will have to register an application on a particular instance. This might vary from instance to instance, but the general idea is that you will have to create an application on the instance you want to use, and then you will be given a client ID and a client secret. You will also have to provide a redirect URI, which is the URL that the instance will redirect you to after you have authenticated.

In my case, I can register an application in my preferences, in the "Development" section. If you are making a project in a git repository, now would be a good time to add two JSON files, one for application credentials, and one for user credentials, to your gitignore. Then, run the following command:

```sh
py -m SlyMastodon scaffold mastodon.skye.vg
```

This will prompt you to name a file path for your application credentials, which will be filled with some data and the correct format to continue. It will be a JSON file.

On the application page for your instance, after you create an application, copy the 'Client key' and 'Client secret' data into your application credentials file into the "id" and "secret" entries, respectively. For the purposes of this tutorial, we will use `http://localhost:8080` as the redirect URI, since that is the default redirect URI for SlyMastodon's CLI granting tool later. Be sure to include this in the 'Redirect URI' field on the application page, and to save your changes.

Once the credentials are saved, you can run the following command to grant access for your application to your account:

```sh
py -m SlyMastodon grant
```

After prompting you for the location to save your user credentials, this will open a browser window to the instance's authentication page, where you will be prompted to log in. After you log in, you will be redirected to a page that hopefully indicates that you have successfully authenticated. You can then close the browser window, and the CLI will fill your credentials with some data and the correct format to continue. It will be a JSON file.

## Using SlyMastodon

Now that you have your credentials, you can use SlyMastodon to access your Mastodon account. The following code will print your username to the console:

```py
import asyncio
from SlyMastodon import *

async def main():
    m = Mastodon( "mastodon.skye.vg",
                  OAuth2("your secret app.json", "your secret user.json") )
    
    user = await m.me()

    print(user.at_username)
asyncio.run(main())
```

It should then output something like:

```sh
@you@skye.vg
```

Because he `Mastodon` class manages async resources such as the connection to the instance, so it should be constructed only after there is an async event loop running. Every API call is already a coroutine function and requres an async event loop to run, so you should be able to use a pattern like the one above. If its strictly necessary, you can [start an event loop](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.set_event_loop) before this yourself, but it is not recommended.