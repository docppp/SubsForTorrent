import logging
from urllib.request import urlopen
from urllib.request import urlretrieve
import cgi
from pathlib import Path

from matcher import Matcher
from scraper import Scraper


class Downloader:

    def __init__(self,
                 file_path: str,
                 rename_sub: bool,
                 override_files: bool,
                 allow_unknown_fps: bool):
        file_path = Path(file_path)
        m = Matcher(file_path)
        q = m.file_info['title'] + " " + str(m.file_info['year']) if 'year' in m.file_info else m.file_info['title']
        # TODO:
        # query for tv series [SomeTvSeriesTitleS01E02]
        scraper = Scraper(q)

        self.chosen_sub = m.get_best_subtitles(scraper.subtitles, allow_unknown_fps)
        self.file_path = file_path
        self.rename_sub = rename_sub
        self.override = override_files
        logging.info(f"CHOOSE: {self.chosen_sub.name}")

    def download_subtitles(self):
        url = self.chosen_sub.link
        directory = self.file_path.parent

        if self.rename_sub:
            filename = Path(self.file_path.stem + self._get_remote_filename(url).suffix)
            full_path = directory.joinpath(filename)
        else:
            full_path = directory.joinpath(self._get_remote_filename(url))

        if full_path.exists() and not self.override:
            logging.warning(f"FOUND: File already exists at {full_path}")
            return

        urlretrieve(url, full_path)
        logging.info(f"SUCCESS: Downloaded subtitle:\n"
                     f"\tname: {self.chosen_sub.name}\n"
                     f"\turl: {url}\n"
                     f"\tpath: {full_path}")

    @staticmethod
    def _get_remote_filename(url):
        remote_file = urlopen(url)
        info = remote_file.info()['Content-Disposition']
        _, params = cgi.parse_header(info)
        return Path(params["filename"])

