import logging
import utilities


def check_movie_page_content(page_text: str):

    if page_text.find("http://schema.org/Movie") == -1:
        # Multiple or zero movies
        logging.warning("NOT FOUND: http://schema.org/Movie")

        if page_text.find("div class=\"msg warn\"") != -1:
            # No movies :(
            logging.error("Cannot match any movie")
            raise utilities.MovieError

        else:
            # More than one movies, need to fix query
            return "MULTI_MOVIES"

    else:
        # Movie match, one or more subtitles
        logging.info("FOUND: http://schema.org/Movie")

        if page_text.find("//dl.opensubtitles.org/") != -1:
            # Only one subtitles
            return "ONE_SUBTITLE"

        else:
            # More than one subtitles
            return "MULTI_SUBTITLES"




