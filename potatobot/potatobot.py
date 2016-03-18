import collections
import functools
import logging
import time

import piazza_api

from .responses import Answer, Followup

PostInfo = collections.namedtuple("PostInfo", ["username", "text", "id", "status"])

class ignore_error:
    def __init__(self, *error_types):
        self._error_types = error_types

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except self._error_types as e:
                logging.info("Ignored error of type {}: {}".format(
                             type(e), str(e)))
        return wrapped


def test_ignore_error():
    @ignore_error(KeyError, ValueError)
    def ignored():
        raise ValueError()

    try:
        ignored()
    except ValueError:
        assert False

    @ignore_error(ValueError, IOError)
    def not_ignored():
        raise KeyError()

    try:
        not_ignored()
        assert False
    except KeyError:
        pass


class PotatoBot:
    POST_LIMIT = 50
    """The number of posts backward in time to search.

    Note that the posts are presented in the same order that you'd see them on
    the web page. That means that the first few will all be announcements. So
    you'll want to set this to something somewhat high."""

    def __init__(self, piazza, user_profile, network):
        """Constructor.

        piazza: The Piazza instance. TODO: This may not be needed.
        user_profile: The Piazza API user profile instance.
        network: The Piazza network for the class.

        """
        self._piazza = piazza
        self._user_profile = user_profile
        self._network = network

        self._post_handlers = []

    @classmethod
    def create_bot(cls, email, password, class_code):
        """Convenience method to create a PotatoBot instance and connect it to
        Piazza.

        email: The email to authenticate with.
        password: The password to authenticate with.
        class_code: The class code that Piazza uses to identify the class. For
            example, the url might look like "piazza.com/class/12345abcde", so
            the class code would be "12345abcde".

        """
        piazza = piazza_api.Piazza()
        piazza.user_login(email=email, password=password)
        user_profile = piazza.get_user_profile()
        network = piazza.network(class_code)
        return PotatoBot(piazza, user_profile, network)

    def _get_new_posts(self):
        """Get new posts on the Piazza class."""
        return self._network.iter_all_posts(limit=self.POST_LIMIT)

    @ignore_error(IOError)
    def _handle_new_posts(self):
        """Go through all the latest posts on Piazza and comment on them."""
        for i in self._get_new_posts():
            if self._should_ignore_post(i):
                continue

            self._handle_single_post(i)

    @ignore_error(KeyError, IndexError)
    def _handle_single_post(self, post):
        """Handle a single Piazza post. Assumes that it has already been
        checked to see if it should be ignored.

        post: The piazza_api post object.

        """
        post_info = self._get_post_info(post)
        responses = (i(post_info) for i in self._post_handlers)
        responses = [i for i in responses if i is not None]

        answers = []
        followups = []
        for i in responses:
            if isinstance(i, Answer):
                answers.append(i)
            elif isinstance(i, Followup):
                followups.append(i)
            else:
                # Assume that it's a follow-up.
                followups.append(Followup(i))

        # Join all answers together since we can only post one answer. But
        # don't try to create an empty answer.
        if answers:
            self._network.create_instructor_answer(
                post,
                "<p></p><p>---</p><p></p>".join(i.text for i in answers),
                revision=0)

        for i in followups:
            self._network.create_followup(post, i.text)

    def _get_post_info(self, post):
        """Returns the `PostInfo` extracted from a post.

        post: The post to extract information from.

        """
        post_history = post["history"][0]
        post_text = post_history["content"]
        post_status = post["status"]

        post_username_id = post_history["uid"]
        post_username = self._network.get_users([post_username_id])
        post_username = post_username[0]["name"]

        return PostInfo(username=post_username,
                        text=post_text,
                        id=post["nr"],
                        status=post_status)

    @ignore_error(KeyError)
    def _should_ignore_post(self, post):
        """Decide whether or not a given post should be ignored. For example,
        if it's an announcement, we probably don't want to respond.

        post: The piazza_api object representing the post.

        """
        if post["bucket_name"] == "Pinned":
            return True

        if post["config"].get("is_announcement", 0) == 1:
            return True

        # Look to see if we've already posted.
        for i in post["children"]:
            if i.get("uid", None) == self._user_profile["user_id"]:
                logging.info("Saw post @{} but ignored it "
                             "because we've already commented on it.".format(
                                 post["nr"]
                                 ))
                return True

        return self.has_answer(post)

    @staticmethod
    def has_answer(post):
        """
        returns whether the given post already has an answer
        """
        return any(d for d in post["change_log"] if d["type"] == "i_answer")

    def handle_post(self, func):
        """Decorates a function to mark it as a handler for PotatoBot posts.

        For example:

            @bot.handle_post
            def handle_post(poster_username, post_text):
                if some_condition():
                    return Followup("response string")
                # Implicitly returning `None` here is okay.

        The return type of the function should be a PotatoBot response, as
        found in `potatobot.responses`. If it is not, it is assumed to be a
        follow-up.

        func: The function to wrap.

        """
        self._post_handlers.append(func)
        return func

    def run_forever(self):
        while True:
            self._handle_new_posts()
            time.sleep(5)
