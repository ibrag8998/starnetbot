import typer

from starnetbot.operations import create_posts, create_users, create_likes
from starnetbot.utils import parse_config
from starnetbot.wrappers import echo


def cli(
    config_path: str = typer.Option(
        './config.json',
        '--config',
        '-c',
        metavar='PATH',
        help='Path to config file (.json)',
    )
):
    echo()

    number_of_users, max_posts_per_user, max_likes_per_user = parse_config(config_path)

    create_users(number_of_users, number_of_users)
    create_posts(max_posts_per_user, max_posts_per_user)
    create_likes(max_likes_per_user, max_likes_per_user)

    echo()


if __name__ == '__main__':
    typer.run(cli)
