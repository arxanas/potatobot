import logging
import re

from potatobot.profile import profile


def has_uniqname(display_name):
    """Whether or not the given user has their uniqname in their Piazza display
    name, as per @6.

    display_name: Their display name on Piazza.

    """
    username_regex = re.compile(r"""
        \(
            [^) ]{1,8} # Their uniqname, in parentheses. There's a maximum
                      # of eight characters in a uniqname.
        \)
    """, re.VERBOSE)

    # Search for their uniqname anywhere in their Piazza display name.
    match = username_regex.search(display_name)
    return match is not None


def is_bad_compiler_error_post(post_text):
    """Detect whether the student is trying to post a message about a compiler
    error, but hasn't actually given us the compiler error."""
    post_text = post_text.lower()
    post_text = post_text.replace("&#39;", "'")

    compile_words = ["compile", "compiling", "compilation"]
    if not any(i in post_text for i in compile_words):
        return False

    # Decide whether it's a post about an error.
    about_error = ["error", "not work", "doesn't work", "won't work",
                   "not compil"]
    if not any(i in post_text for i in about_error):
        return False

    # Now, see if they've actually given us anything to work with.
    provided_error = ["<code", "<pre", "<img", ": error:"]
    if any(i in post_text for i in provided_error):
        return False

    return True


def cant_valgrind(post_text):
    """Whether or not the student is trying to debug a segfault but hasn't
    tried valgrind."""
    post_text = post_text.lower()

    segfault_error = ["segv", "segfault"]
    if not any(i in post_text for i in segfault_error):
        return False

    if "valgrind" in post_text:
        return False

    return True


@profile("EECS281_PBOT")
def eecs281_profile(bot):
    logging.basicConfig(level=logging.DEBUG)

    @bot.handle_post
    def demand_uniqname(poster_username, post_text):
        if not has_uniqname(poster_username):
            return """
<p>Hi! It looks like you don't have your uniqname in your display name, as per
@6. Please add it so that we can look you up on the autograder quickly.</p>
"""

    @bot.handle_post
    def complain_about_compiler_errors(poster_username, post_text):
        if is_bad_compiler_error_post(post_text):
            return """
<p>Hi! It looks like you have a compiler error, but you didn't tell us what the
error was! (Or if you did, you didn't paste it into a code block so that we
could read it easily.) We'll need to see the <em>full</em> compile error
output, so please add it.</p>
<p></p>
<p>If you don't have a compiler error, sorry about that! I'm just a potato; I
can't read very well.</p>
"""

    @bot.handle_post
    def learn_to_valgrind_please(poster_username, post_text):
        if cant_valgrind(post_text):
            return """
<p>It looks like you're having an issue with a segfault! Have you run your code
under valgrind? If you don't know how to use valgrind, read this: <a
href="http://maintainablecode.logdown.com/posts/245425-valgrind-is-not-a-leak-checker">Valgrind
is not a leak-checker</a>.</p>
<p></p>
<p>Once you've valgrinded your code, post the full valgrind output and the
relevant lines of code. (Make sure that you compile <code>make debug</code> so
that valgrind shows you line numbers.)</p>
<p></p>
<p>If valgrind doesn't show anything, that probably means you need better test
cases!</p>
"""

    @bot.handle_post
    def hi_me(poster_username, post_text):
        if "wkhan" in poster_username:
            return "Test post!"
