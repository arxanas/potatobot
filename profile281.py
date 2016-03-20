import jsim
import logging
import os
import re
import sys

from potatobot import Answer, Followup, PotatoBot

JSIM_FILE = "eecs281jsim.json"
JSIM_THRESHOLD = .25
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


def has_uniqname(display_name):
    """Whether or not the given user has their uniqname in their Piazza display
    name, as per @6.

    display_name: Their display name on Piazza.

    """
    if "Piazza Team" in display_name:
        return True

    username_regex = re.compile(r"""
        \(
            [^) ]{1,8} # Their uniqname, in parentheses. There's a maximum
                      # of eight characters in a uniqname.
        \)
    """, re.VERBOSE)

    # Search for their uniqname anywhere in their Piazza display name.
    match = username_regex.search(display_name)
    return match is not None


def test_has_uniqname():
    assert not has_uniqname("Waleed Khan")
    assert has_uniqname("Waleed Khan (wkhan)")
    assert has_uniqname("(wkhan)")
    assert not has_uniqname("(wkhan")
    assert not has_uniqname("( wkhan )")


def test_has_uniqname_ignores_special_usernames():
    assert has_uniqname("Piazza Team")


def is_bad_compiler_error_post(post_text):
    """Detect whether the student is trying to post a message about a compiler
    error, but hasn't actually given us the compiler error."""
    post_text = post_text.lower()
    post_text = post_text.replace("&#39;", "'")

    if "#compiler-error" in post_text:
        return True

    compile_words = ["compile", "compiling", "compilation"]
    if not any(i in post_text for i in compile_words):
        return False

    # Decide whether it's a post about an error.
    about_error = ["error", "not work", "doesn't work", "won't work",
                   "not compil", "complain"]
    if not any(i in post_text for i in about_error):
        return False

    # Now, see if they've actually given us anything to work with.
    provided_error = ["<code", "<pre", "<img", ": error:"]
    if any(i in post_text for i in provided_error):
        return False

    return True


def test_is_bad_compiler_error_post():
    assert is_bad_compiler_error_post("regular post #compiler-error")
    assert is_bad_compiler_error_post("Compile error")
    assert is_bad_compiler_error_post("compile doesn't work")
    assert is_bad_compiler_error_post("compile doesn&#39;t work")
    assert is_bad_compiler_error_post("not working compiler")
    assert is_bad_compiler_error_post("not compiling")
    assert is_bad_compiler_error_post("compiler complaining")
    assert not is_bad_compiler_error_post("compilers are great")
    assert not is_bad_compiler_error_post("my code isn't working")
    assert not is_bad_compiler_error_post("not working compile message <pre>")
    assert not is_bad_compiler_error_post("not working compile message <code>")
    assert not is_bad_compiler_error_post("error compile message <img src>")
    assert not is_bad_compiler_error_post("not compiling 90: error:")


def cant_valgrind(post_text):
    """Whether or not the student is trying to debug a segfault but hasn't
    tried valgrind."""
    post_text = post_text.lower()

    if "#valgrind" in post_text:
        return True

    segfault_error = ["segv", "sigsev", "sig sev",
                      "segfault", "seg fault",
                      "segmentation"]
    if not any(i in post_text for i in segfault_error):
        return False

    if "valgrind" in post_text:
        return False

    return True


def test_cant_valgrind():
    assert cant_valgrind("regular post #valgrind")
    assert cant_valgrind("SIG SEV but don't know why")
    assert cant_valgrind("SIGSEV but don't know why")
    assert cant_valgrind("SIGSEGV but don't know why")
    assert cant_valgrind("my program segfaults")
    assert cant_valgrind("my program seg faults")
    assert cant_valgrind("I have a segmentation issue")
    assert not cant_valgrind("segfault valgrind doesn't help")
    assert not cant_valgrind("my program sucks")



def main():
    logging.basicConfig(level=logging.DEBUG)
    bot = get_bot()

    @bot.handle_post
    def demand_uniqname(post_info):
        if not has_uniqname(post_info.username):
            return Answer("""
<p>Hi! It looks like you don't have your uniqname in your display name, as per
@6. Please add it so that we can look you up on the autograder quickly.</p>
""")

    @bot.handle_post
    def complain_about_compiler_errors(post_info):
        if is_bad_compiler_error_post(post_info.text):
            return Answer("""
<p>Hi! It looks like you have a compiler error, but you didn't tell us what the
error was! (Or if you did, you didn't paste it into a code block so that we
could read it easily.) We'll need to see the <em>full</em> compile error
output, so please add it.</p>
<p></p>
<p>Here are some guidelines you will need to follow if you are to receive help:

<ul>
  <li>Paste the <strong>FULL COMPILER ERROR</strong> from g++. Do not omit any
  part.</li>
  <li>Do not paste compiler errors from Visual Studio or Xcode, as they are
  usually one line long and not informative. Please compile your code under
  g++, as it provides infinitely more helpful compiler error messages.</li>
  <li>Do not post part of the compiler error from g++ and say that the rest is
  similar to it. That is not helpful and someone on staff will scowl at you.
  Paste the entire compiler error output, even the parts you think are not
  important.</li>
  <li>Even if you think your question can be answered without looking at the
  compiler error message, please post it anyways.</li>
</ul>

<p></p>
<p>If you don't have a compiler error, sorry about that! I'm just a potato; I
can't read very well.</p>
""")

    @bot.handle_post
    def learn_to_valgrind_please(post_info):
        if cant_valgrind(post_info.text):
            return Answer("""
<p>It looks like you're having an issue with a segfault! Have you run your code
under valgrind? If you don't know how to use valgrind, read this: <a
href="http://maintainablecode.logdown.com/posts/245425-valgrind-is-not-a-leak-checker">Valgrind
is not a leak-checker</a>.</p>
<p></p>
<p>Having no memory leaks does not indicate that your program is safe. Read the
above article.</p>
<p></p>
<p>Once you've valgrinded your code, post the full valgrind output and the
relevant lines of code. (Make sure that you compile <code>make debug</code> so
that valgrind shows you line numbers.) <strong>We will not answer your question
until you post valgrind output</strong>.</p>
<p></p>
<p>If valgrind doesn't show anything, that probably means you need better test
cases!</p>
""")

    @bot.handle_post
    def check_for_duplicate_posts(post_info):
        if post_info.status != "private":

            jsim.save(JSIM_FILE, post_info.id, post_info.text)

        sim_list = jsim.getSimilarities(JSIM_FILE, post_info.id, post_info.text, JSIM_THRESHOLD)

        sim_list = [i for i in sim_list if int(i[1]) < post_info.id]
        answers = ", ".join("@" + x[1] for x in sim_list[:JSIM_LIMIT])
        if sim_list:
            return Followup("""
<p>Hi! It looks like this question has been asked before or there is a related post.
Please look at these posts: {}</p>
<p></p>
<p>If you found your answer in one of the above, please specify which one answered your question.</p>
""".format(answers))

    bot.run_forever()

if __name__ == "__main__":
    main()
