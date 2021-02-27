import random

from starnetbot.api import starnet_api
from starnetbot.utils import random_str, g
from starnetbot.wrappers import echo, styled, BRIGHT_CYAN, RED


class MassOperationCrash(BaseException):
    ...


class MassOperation:
    """
    Hooks:

        - .set_up() - called before the loop will start
        - .tear_down() - called after loop ends
        - .core() - called in each iteration of a loop
        - .on_crash() - called on MassOperationCrash
        - .on_max_crashes() - called if max crashes limit exceeded
    """

    i: int = 0
    crashes: int = 0

    def __call__(self, n_iterations: int, crashes_limit: int = None) -> None:
        self.set_up()

        self.i = 0
        self.crashes = 0
        while self.i < n_iterations:
            try:
                self.core()
            except MassOperationCrash:
                self.crashes += 1
                self.on_crash()

                if crashes_limit is not None:  # means there are no limit
                    if self.crashes > crashes_limit:
                        self.on_max_crashes()
                        break
            else:
                self.i += 1

        self.tear_down()

    def set_up(self):
        ...

    def tear_down(self):
        ...

    def core(self):
        raise NotImplementedError()

    def on_crash(self):
        echo(styled("Error occurred! Retrying...", fg=RED))

    def on_max_crashes(self):
        echo(styled("\n\nSomething went wrong, stopping operation...\n", fg=RED))

    def crash(self, really: bool = True) -> None:
        if really:
            raise MassOperationCrash()


class CreateUsersOperation(MassOperation):
    def __call__(self, n_iterations: int, crashes_limit: int = None) -> None:
        super().__call__(n_iterations, n_iterations)

    def set_up(self):
        self.users = []

    def core(self):
        credentials = {'username': random_str(), 'password': random_str(min_length=8)}
        response = starnet_api.post('/users/', data=credentials)

        self.crash(not response.ok)

        self.users.append(credentials)
        echo("Successfully created user #{}.".format(styled(str(self.i + 1), fg=BRIGHT_CYAN)))

    def tear_down(self):
        echo("===\nSuccessfully created {} users\n".format(styled(str(len(self.users)), fg=BRIGHT_CYAN)))
        g.users = self.users[:]


class CreatePostsOperation(MassOperation):
    def __call__(self, n_iterations: int, crashes_limit: int = None) -> None:
        self.posts = []

        for j, user in enumerate(g.get('users')):
            starnet_api.user(**user)

            # get random number of posts to create for current user
            number_of_posts = random.randrange(0, n_iterations + 1)
            echo("Creating {} posts from user #{}...".format(
                styled(str(number_of_posts), fg=BRIGHT_CYAN),
                styled(str(j + 1), fg=BRIGHT_CYAN)
            ))

            super().__call__(number_of_posts, number_of_posts)

        echo("===\nSuccessfully created {} posts\n".format(styled(str(len(self.posts)), fg=BRIGHT_CYAN)))

    def core(self):
        response = starnet_api.post('/posts/', data={'content': random_str()}, auth=True)

        self.crash(not response.ok)

        self.posts.append(response.json()['id'])

    def tear_down(self):
        g.posts = self.posts[:]


class CreateLikesOperation(MassOperation):
    def __call__(self, n_iterations: int, crashes_limit: int = None) -> None:
        self.likes = 0  # to count total likes for all users
        posts = g.get('posts')

        for j, user in enumerate(g.get('users')):
            starnet_api.user(**user)

            # get random number of likes to create for current user
            # number of likes cannot be bigger than number of posts,
            # because one user cannot like the post twice.
            number_of_likes = random.randrange(0, min(n_iterations, len(posts)) + 1)
            echo("Liking {} posts as user #{}...".format(
                styled(str(number_of_likes), fg=BRIGHT_CYAN),
                styled(str(j + 1), fg=BRIGHT_CYAN)
            ))

            self.posts_to_like = random.sample(posts, number_of_likes)  # len is equal to `number_of_likes`

            super().__call__(number_of_likes, number_of_likes)

        echo("===\nSuccessfully liked {} posts\n".format(styled(str(self.likes), fg=BRIGHT_CYAN)))

    def core(self):
        post_id = self.posts_to_like[self.i]
        response = starnet_api.post(f'/posts/{post_id}/like/', auth=True)

        self.crash(not response.ok)

        self.likes += 1


create_users = CreateUsersOperation()
create_posts = CreatePostsOperation()
create_likes = CreateLikesOperation()
