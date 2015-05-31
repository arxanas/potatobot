"""Create a new bot profile, using credentials from the environment."""

import os
import sys

from potatobot import PotatoBot


def die(message):
    sys.stderr.write("{}\n".format(message))
    sys.exit(1)


def get_bot(env_prefix):
    """Get the PotatoBot instance from enviroment variables prefixed with the
    given prefix.

    The following values in the environment must be set:

      * `PREFIX_EMAIL`
      * `PREFIX_PASSWORD`
      * `PREFIX_CLASS_CODE`

    env_prefix: The prefix to insert for `PREFIX` above.

    """
    config_sources = {
        "email": "_EMAIL",
        "password": "_PASSWORD",
        "class_code": "_CLASS_CODE",
    }
    config_sources = {i: env_prefix + j for i, j in config_sources.items()}

    config = {}
    for var, source in config_sources.items():
        try:
            config[var] = os.environ[source]
        except KeyError:
            die("`{}` must be set in the environment.".format(
                source
            ))

    return PotatoBot.create_bot(**config)


class Profile:
    """A bot profile object. The `profile` decorator below generates one of
    these.

    """
    def __init__(self, func):
        self._func = func

    def __call__(self):
        self._func()


class profile:
    """Register and launch a new PotatoBot profile.

    Usage:

    ```
    @bot
    def my_bot(bot):
        @bot.handle_post
        def always_reply_foo():
            return "foo"

        @bot.handle_pots
        def always_reply_bar():
            return "bar"
    ```

    """
    def __init__(self, env_prefix):
        self._env_prefix = env_prefix

    def __call__(self, profile_func):
        def ret():
            bot = get_bot(self._env_prefix)
            profile_func(bot)
            bot.run_forever()
        return Profile(ret)
