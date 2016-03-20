"""The various types of responses that PotatoBot can reply with.

PotatoBot will not reply if there is already a follow-up by PotatoBot or if
there is an instructor answer (by anyone -- we don't want to overwrite it).
"""

class Answer:
    """An instructor answer.

    Instructor answer responses are aggregated into one answer (because there
    is only space for one answer) and separated by a delimiter.

    text: The text of the answer.

    """

    def __init__(self, text):
        self.text = text


class Followup:
    """A follow-up question.

    Any follow-up questions triggered by a post are triggered separately. They
    are unresolved by default.

    text: The text of the follow-up.

    """

    def __init__(self, text):
        self.text = text
