import logging
import shutil
from pathlib import Path

from requests import Session as HTTPSession, Response
from requests.auth import HTTPBasicAuth

log = logging.getLogger("http")


class Connection:

    def __init__(self, username: str, password: str):
        self.session = HTTPSession()
        self.session.auth = HTTPBasicAuth(username, password)

    def _get_url(self, url: str) -> str:
        if not url.startswith("http"):
            if url.startswith("/FIT/st/"):
                return f"https://wis.fit.vutbr.cz{url}"
            elif url.startswith("/st/"):
                return f"https://wis.fit.vutbr.cz/FIT{url}"
            else:
                return f"https://wis.fit.vutbr.cz/FIT/st/{url}"

        return url

    def _get(self, url: str, params: dict[str, str], stream: bool = False) -> Response:
        """ Makes an HTTP GET request to the given URL and ensures the response is valid. """
        url = self._get_url(url)
        response = self.session.get(url, params=params, stream=stream)
        response.raise_for_status()

        return response

    def get_content(self, url: str, **params: [str, int]) -> str:
        """ Loads and returns contents of the given webpage. """
        with self._get(url, params) as response:
            return response.content.decode("iso-8859-2")

    def get_studies_page(self) -> str:
        return self.get_content("study-s.php.cs")

    def get_courses_page(self, study: int = 1) -> str:
        assert study > 0
        return self.get_content("study-a.php.cs", cist=study)

    def download_file(self, link: str, filepath: Path):
        with self._get(link, {}, stream=True) as response:
            log.debug("downloading %s -> %s", link, filepath.as_posix())
            with filepath.open("wb") as file:
                for chunk in response.iter_content(chunk_size=128 * 1024):
                    if chunk:
                        file.write(chunk)

        log.info("successfully downloaded %s", filepath.as_posix())

    def close(self):
        self.session.close()
