# This is a dev hack not something for production

# How to run:
# python3 cli/create_user.py name password -r user

import argparse

from auth.auth import register_user


def main():
    parser = argparse.ArgumentParser(description="Create a new user for LogTrack")
    parser.add_argument("username", help="Username for the new user")
    parser.add_argument("password", help="Password for the new user")
    parser.add_argument(
        "-r",
        "--role",
        choices=["user"],  # "admin" add later
        default="user",
        help="Role for the new user (default: user)",
    )
    args = parser.parse_args()

    register_user(args.username, args.password, args.role)


if __name__ == "__main__":
    main()
