from dataclasses import asdict, dataclass
from enum import Enum
from datetime import datetime
from typing import Generic, TypeVar
from SlyMastodon import *
import SlyMastodon.serialization as ser
from SlyAPI.web import JsonType

def test_de_simple():

    for x in (None, 1, 2.5, "hi", True):
        assert x == ser.convert_from_json(type(x), x)

def test_de_list():
    x: list[JsonType] = [1, 2, 3]
    assert x == ser.convert_from_json(list[int], x)

def test_de_set():
    x = {1, 2, 3}
    assert x == ser.convert_from_json(set[int], list(x))

def test_de_tuple():
    x = (1, 2.5, "hi")
    assert x == ser.convert_from_json(tuple[int, float, str], list(x))

def test_de_dict():
    x: JsonType = {"a": 1, "b": 2, "c": 3}
    assert x == ser.convert_from_json(dict[str, int], x)

def test_de_enum():
    class Test(Enum):
        A = 1
        B = 2

    x = Test.A
    assert x == ser.convert_from_json(Test, x.value)

def test_de_union():
    x = 1
    assert x == ser.convert_from_json(int | str, x)

def test_de_dataclass():
    @dataclass
    class Test:
        a: int
        b: str
        c: JsonType

    x = Test(1, "hi", {'x': 1, 'y': {}, 'z': [None, 2.5]})
    assert x == ser.convert_from_json(Test, asdict(x))

T = TypeVar('T')
U = TypeVar('U')

ListSet = tuple[list[T], set[T]]

def test_de_generic_alias():
    x: ListSet[int] = ([1, 2, 2], {1, 2})
    assert x == ser.convert_from_json(ListSet[int], list(map(list, x)))

def test_de_generic_gerneric_arg():
    @dataclass
    class Test(Generic[T]):
        a: T
    x = Test[Test[int]](Test[int](1))
    assert x == ser.convert_from_json(Test[Test[int]], asdict(x))
    x = Test[list[int]]([1, 2, 3])
    assert x == ser.convert_from_json(Test[list[int]], asdict(x))

def test_de_delayed_gerneric():
    @dataclass
    class Test(Generic[T]):
        a: 'list[T]'
        b: 'T'
    x = Test[Test[int]]([Test[int]([1], 2)], Test[int]([3], 4))
    assert x == ser.convert_from_json(Test[Test[int]], asdict(x))
    x = Test[list[int]]([[1, 2, 3]], [])
    assert x == ser.convert_from_json(Test[list[int]], asdict(x))

def test_de_dataclass_generic():

    @dataclass
    class Test(Generic[T]):
        a: T
        b: list[T]
        c: dict[str, T]

    x = Test[int](1, [2, 3], {'x': 1, 'y': 2, 'z': 3})
    assert x == ser.convert_from_json(Test[int], asdict(x))

def test_de_datetime():
    x = datetime.now()
    assert x == ser.convert_from_json(datetime, x.isoformat())
    assert x == ser.convert_from_json(datetime, x.timestamp())

def test_de_post():

    x: JsonType = {
        'id': '109958407801025523', 'created_at': '2023-03-03T08:29:10.291Z',
        'in_reply_to_id': None, 'in_reply_to_account_id': None,
        'sensitive': False, 'spoiler_text': '', 'visibility': 'public',
        'language': 'en',
        'uri': \
            'https://mastodon.skye.vg/users/dunkyl/statuses/109958407801025523',
        'url': 'https://mastodon.skye.vg/@dunkyl/109958407801025523', 
        'replies_count': 0, 'reblogs_count': 0, 'favourites_count': 0, 
        'edited_at': None, 'favourited': False, 'reblogged': False,
        'muted': False,'bookmarked': False, 'pinned': False, 'local_only': None, 'content': '<p>test 4</p>', 'filtered': [], 'reblog': None, 
        'application': {
            'name': 'SlyMastodon Test', 
            'website': 'https://github.com/dunkyl/SlyMastodon'
        },
        'account': {
            'id': '109289749579593700', 'username': 'dunkyl', 'acct': 'dunkyl',
            'display_name': 'Dunkyl 🔣🔣', 'locked': False, 'bot': False,
            'discoverable': True, 'group': False,
            'created_at': '2022-11-05T00:00:00.000Z', 'note': '',
            'url': 'https://mastodon.skye.vg/@dunkyl',
            'avatar': \
                'https://mastodon-cdn.skye.vg/accounts/avatars/109/289/749/579/593/700/original/1e2288841aab39a6.png',
            'avatar_static': \
                'https://mastodon-cdn.skye.vg/accounts/avatars/109/289/749/579/593/700/original/1e2288841aab39a6.png',
            'header': \
                'https://mastodon-cdn.skye.vg/accounts/headers/109/289/749/579/593/700/original/0b27b0466b0d259f.jpg',
            'header_static': \
                'https://mastodon-cdn.skye.vg/accounts/headers/109/289/749/579/593/700/original/0b27b0466b0d259f.jpg',
            'followers_count': 5, 'following_count': 22, 'statuses_count': 31,
            'last_status_at': '2023-03-03', 'noindex': False, 'emojis': [],
            'roles': [], 'fields': []
        }, 
        'media_attachments': [], 'mentions': [], 'tags': [], 'emojis': [], 
        'reactions': [], 'card': None, 'poll': None, 'quote': None
    }

    ser.convert_from_json(Post|None, x)