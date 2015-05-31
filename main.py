import logging

from potatobot.profile import Profile
import profiles


def main():
    logging.basicConfig(level=logging.DEBUG)

    # Scan for profile objects, and then run any that we find.
    # TODO: If there are multiple, we'll actually want to run them in parallel.
    for i in dir(profiles):
        potential_profile = getattr(profiles, i)
        if isinstance(potential_profile, Profile):
            potential_profile()

if __name__ == "__main__":
    main()
