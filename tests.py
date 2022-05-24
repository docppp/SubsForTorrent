import logging
import unittest

import utilities
from pageinfo import check_page_content
from scraper import Scraper
from subtitle import Subtitle

#
# Test pages can change in the future as new subtitles could be uploaded,
# but testing not on the live page does not make much sense.
#
# If any test fail, manual check if something changed should be done first.
#
# Assumptions:
# Query "Men in hope 2010" is invalid.
# Query "Men in hope" gives 2 movies - "Men in Hope" and "Men in Black".
# Query "Men in hope 2011" gives only one movie with 3 different subtitles.
# Query "Moana 2016" redirects directly to subtitle site (ony one subtitle).
# Query "Solar.Opposites.S01E01" is tv series with id 929902 and one subtitle.
#


class Pages:
    logging.basicConfig(level=logging.CRITICAL)
    address = "https://www.opensubtitles.org/pl/search2/sublanguageid-pol/moviename-"
    q_zero_movies = "Men in hope 2010"
    q_multi_movies = "Men in hope"
    q_multi_subs = "Men in hope 2011"
    q_one_sub = "Moana 2016"
    q_tv_series = "Solar.Opposites.S01E01"
    zero_movies = utilities.get_page(address + q_zero_movies)
    multi_movies = utilities.get_page(address + q_multi_movies)
    multi_subs = utilities.get_page(address + q_multi_subs)
    one_sub = utilities.get_page(address + q_one_sub)
    tv_series_first = utilities.get_page(address + q_tv_series)
    tv_series_second = utilities.get_page("https://www.opensubtitles.org/pl/search/sublanguageid-pol/idmovie-929902")


class TestPageInfo(unittest.TestCase):
    def test_page_info_movie(self):
        self.assertEqual(check_page_content(Pages.multi_movies.text), "MULTI_MOVIES")
        self.assertEqual(check_page_content(Pages.multi_subs.text), "MULTI_SUBTITLES")
        self.assertEqual(check_page_content(Pages.one_sub.text), "ONE_SUBTITLE")
        with self.assertRaises(utilities.MovieError):
            check_page_content(Pages.zero_movies.text)

    def test_page_info_tv_series(self):
        self.assertEqual(check_page_content(Pages.tv_series_first.text), "MULTI_MOVIES")
        self.assertEqual(check_page_content(Pages.tv_series_second.text), "TV_SERIES")


class TestScraper(unittest.TestCase):
    def test_subtitles_on_the_page(self):
        subtitles = Scraper.find_multi_subs(Pages.multi_subs.content)
        self.assertEqual(len(subtitles), 3)
        self.assertEqual(subtitles[0].name, "psig-muzi.v.nadeji.2011.dvdrip.xvid")
        self.assertEqual(subtitles[1].name, "Muzi.v.nadeji.2011.DVDRip.XviD.AC3.CZ.LEADERs")
        self.assertEqual(subtitles[2].name, "Muzi.v.nadeji.2011.x264.DTS-WAF")

    def test_single_subtitle_ont_the_page(self):
        subtitles = Scraper.find_single_sub(Pages.one_sub.text)
        self.assertEqual(len(subtitles), 1)
        self.assertEqual(subtitles[0].name, "Moana.2016.MULTi.1080p.BluRay.DTS.x264-TPX.srt")

    def test_scraper_live_test_tv_series(self):
        s = Scraper("Solar Opposites", 1, 1)
        self.assertEqual(len(s.subtitles), 1)
        self.assertEqual(s.subtitles[0].name, "Solar.Opposites.S01E01.720p.HULU.WEBRip.x264-GalaxyTV.srt")

    def test_scraper_live_test_multi_sub(self):
        s = Scraper("Men in hope")
        self.assertEqual(len(s.subtitles), 3)

    # TODO:
    # test choose_one_query, also splitting this func for smaller pieces would be nice


class TestSubtitle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sub = Subtitle("psig-muzi.v.nadeji.2011.dvdrip.xvid", "4466472")

    def test_fps(self):
        self.assertEqual(self.sub.get_subtitle_fps(), 25)

    def test_link(self):
        self.assertEqual(self.sub.get_subtitle_link(), "https://dl.opensubtitles.org/pl/download/file/1953027826")


# TODO:
# test Matcher

if __name__ == '__main__':
    unittest.main()
