import logging
import re
from urllib import parse

from bs4 import BeautifulSoup

import utilities
from pageinfo import check_page_content
from subtitle import Subtitle


class Scraper:
    def __init__(self, query: str, season: int = 0, episode: int = 0):
        logging.info(f"QUERY: {query}")
        self.query = query
        self.address = f"https://www.opensubtitles.org/pl/search2/sublanguageid-pol/moviename-{parse.quote(query)}"
        self.page = utilities.get_page(self.address)
        self.season = season
        self.episode = episode

        where_am_i = check_page_content(self.page.text)

        if where_am_i == "MULTI_MOVIES":
            self.query, movie_id = self.choose_one_query()
            self.address = f"https://www.opensubtitles.org/pl/search/sublanguageid-pol/idmovie-{movie_id}"
            self.page = utilities.get_page(self.address)
            where_am_i = check_page_content(self.page.text)

        logging.info(f"SUCCESS: OpenSubtitles entry:\n"
                     f"\tquery: {self.query}\n"
                     f"\taddress: {self.address}")

        if where_am_i == "TV_SERIES":
            episode_id = self.choose_one_episode()
            self.address = f"https://www.opensubtitles.org/pl/search/sublanguageid-pol/imdbid-{episode_id}"
            self.page = utilities.get_page(self.address)
            where_am_i = check_page_content(self.page.text)

        if where_am_i == "MULTI_SUBTITLES":
            self.subtitles = self.find_multi_subs(self.page.content)
        elif where_am_i == "ONE_SUBTITLE":
            self.subtitles = self.find_single_sub(self.page.text)
        else:
            logging.error("Something went wrong, dunno where am i")
            raise LookupError

    def choose_one_query(self):
        # Extract movie queries
        soup = BeautifulSoup(self.page.content, "html.parser")
        results = soup.find(id="search_results")
        movies_html = results.find_all("strong")
        movies = [m.text for m in movies_html]
        movies_log = [m.replace('\n', ' ') for m in movies]
        logging.info(f"FOUND: {len(movies_html)} movies: {movies_log}")

        # Calculate score and choose best
        scores = [utilities.damerau_levenshtein(title, self.query) for title in movies_log]
        new_query = movies[scores.index(min(scores))]
        new_query_log = new_query.replace('\n', ' ')
        logging.info(f"CHOOSE: {new_query_log}")

        # Get chosen movie id
        regex = r'idmovie-[0-9]*">' + re.escape(new_query)
        r = re.search(regex, self.page.text)
        movie_id = r.group(0).split('"')[0].split('-')[1]
        return new_query_log, movie_id

    def choose_one_episode(self):
        # Get correct season
        soup = BeautifulSoup(self.page.content, "html.parser")
        results = soup.find(id=f"season-{self.season}").parent.parent

        # Get correct episode in that season
        for _ in range(self.episode):
            results = results.next_sibling

        # Get episode id
        r = re.search('/search/sublanguageid-pl/imdbid-[0-9]*', str(results))
        episode_id = r.group(0).split('/')[-1].split('-')[-1]
        return episode_id

    @staticmethod
    def find_multi_subs(page_content: bytes):
        # Extract subtitles name and id
        soup = BeautifulSoup(page_content, "html.parser")
        results = soup.find(id="search_results")
        subtitles_html = results.find_all("strong")

        names = [s.parent.findNext("br").next_element.text for s in subtitles_html]
        ids = [''.join(i for i in s.parent.get("id") if i.isdigit()) for s in subtitles_html]

        logging.info(f"FOUND: {len(ids)} subtitles: {ids}")
        return Scraper._subtitles_from_id_and_name(names, ids)

    @staticmethod
    def find_single_sub(page_text: str):
        r = re.search('ret="/pl/subtitles/[0-9]*/', page_text)
        ids = [r.group(0).split('/')[-2]]

        r = re.search('star-off.gif" alt=".*" title=".*".*\n', page_text)
        names = [r.group(0).split('>')[-1].strip()]

        logging.info(f"FOUND: 1 subtitles: {ids}")
        return Scraper._subtitles_from_id_and_name(names, ids)

    @staticmethod
    def _subtitles_from_id_and_name(names: list, ids: list) -> list[Subtitle]:
        # Prepare subtitles with link and fps
        subtitles = [Subtitle(n, i) for n, i in zip(names, ids)]
        for s in subtitles:
            logging.info(f"FOUND: {s}")
        return subtitles

