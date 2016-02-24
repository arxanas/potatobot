import jsim
import logging
import os
import re
import sys

from potatobot import PotatoBot

JSIM_FILE = "posts183.json"
JSIM_THRESHOLD = .32
JSIM_LIMIT = 50

def die(message):
    sys.stderr.write("{}\n".format(message))
    sys.exit(1)


def get_bot():
    config_sources = {
        "email": "PBOT_EMAIL",
        "password": "PBOT_PASSWORD",
        "class_code": "PBOT_CLASS_CODE",
    }

    config = {}
    for var, source in config_sources.items():
        try:
            config[var] = os.environ[source]
        except KeyError:
            die("`{}` must be set in the environment.".format(
                source
            ))

    return PotatoBot.create_bot(**config)




def main():
    logging.basicConfig(level=logging.INFO)
    bot = get_bot()

    @bot.handle_post
    def check_for_duplicate_posts(post_info):
        if post_info.status != "private":
            
            jsim.save(JSIM_FILE, post_info.id, post_info.text)
        
        sim_list = jsim.getSimilarities(JSIM_FILE, post_info.id, post_info.text, JSIM_THRESHOLD)
        
        sim_list = [i for i in sim_list if int(i[1]) < post_info.id]
        answers = ", ".join("@" + x[1] for x in sim_list[:JSIM_LIMIT])
        if sim_list:
            return """
<p>Hi! It looks like this question has been asked before or there is a related post.
You may find these posts helpful: {}</p>
<p></p>
<p>If you found your answer in one of the above, please mark your question as a note 
to resolve it / specify which one answered your question. </p>
""".format(answers)

    bot.run_forever()

if __name__ == "__main__":
    main()
