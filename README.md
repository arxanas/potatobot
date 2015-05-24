# About

PotatoBot is a Piazza bot to automatically respond to questions.

# Installation

PotatoBot is written for Python 3.

# Usage

Set up configuration values in `profile.py`:

```
import potatobot

bot = potatobot.PotatoBot(
    username="potatobot",
    password="gr34tp4$$w0rd"
)

@bot.handle_post
def some_handler(poster_username, poster_text):
    if should_respond():
        return "String to respond with"
    # Implicitly return `None` -- don't respond.

# Runs forever.
bot.run()
```
