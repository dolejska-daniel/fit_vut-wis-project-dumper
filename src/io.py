import logging
import re
import sys
from getpass import getpass
from gettext import gettext

log = logging.getLogger("io")


def get_user_credentials() -> (str, str):
    log.debug("loading user credentials")

    username, password = "", ""
    while re.fullmatch(r"^x[a-z]{5}[a-z\d]{2}$", username) is None:
        username = input("WIS username: ")

    while len(password) < 10:
        password = getpass("WIS password: ", sys.stdout)

    log.debug("credentials successfully obtained: username=%s, password=%s", username, password)
    return username, password
