# About

PotatoBot is a Piazza bot to automatically respond to questions. It's
specifically written for EECS 281 at the University of Michigan.

# Installation

PotatoBot is written for Python 3.

Make sure to init the `piazza-api` submodule:

```
git submodule update --init --recursive
```

# Usage

Set up configuration values in `profile.py`:

```
import piazza_api
import potatobot

piazza = piazza_api.Piazza(
    email="potatobot",
    password="gr34tp4$$w0rd"
)
bot = potatobot.PotatoBot(piazza)

@bot.handle_post
def some_handler(poster_username, post_text):
    if "help" in poster_text:
        return "It looks like you need help!"
    # Implicitly return `None` -- don't respond.

bot.run_forever()
```
