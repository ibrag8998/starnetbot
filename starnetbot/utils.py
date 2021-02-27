import json
import random
from typing import Tuple


def parse_config(config_path: str) -> Tuple[int, int, int]:
    if not config_path.endswith('.json'):
        raise ValueError("Only .json files are supported")

    with open(config_path) as f:
        config = json.load(f)

    # beware of KeyError
    return config['number_of_users'], config['max_posts_per_user'], config['max_likes_per_user']


def random_str(min_length: int = 1, max_length: int = 150, symbols: str = None):
    symbols = symbols or '0123456789' 'qwertyuiopasdfghjklzxcvbnm' 'QWERTYUIOPASDFGHJKLZXCVBNM' '-_'
    return ''.join(random.choice(symbols) for _ in range(random.randrange(min_length, max_length)))


class empty:  # noqa
    ...


class GlobalStorage:
    def get(self, what: str, default=empty):
        if default is empty:
            try:
                return getattr(self, what)
            except AttributeError as e:
                raise AttributeError(f"There are no `{what}` in global storage") from e

        return getattr(self, what, default)


g = GlobalStorage()
