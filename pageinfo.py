import logging
import utilities


def check_page_content(page_text: str):

    if page_text.find("http://schema.org/Movie") == -1:
        # schema.org/Movie cannot be found: Multiple or zero movies or tv series
        logging.warning("NOT FOUND: http://schema.org/Movie")

        if page_text.find("div class=\"msg warn\"") != -1:
            # No movies :(
            logging.error("Cannot match any movie")
            raise utilities.MovieError

        elif page_text.find("http://schema.org/TVSeries") == -1:
            # Not a tv series and more than one movies, need to fix query
            logging.info("FOUND: Multi movies")
            return "MULTI_MOVIES"

        else:
            # schema.org/TVSeries found: Must be tv series
            logging.info("FOUND: Tv Series")
            return "TV_SERIES"

    else:
        # schema.org/Movie found: Movie match, one or more subtitles
        logging.info("FOUND: http://schema.org/Movie")

        if page_text.find("//dl.opensubtitles.org/") != -1:
            # Only one subtitles
            logging.info("FOUND: Only one subtitle")
            return "ONE_SUBTITLE"

        else:
            # More than one subtitles
            logging.info("FOUND: Multi subtitles")
            return "MULTI_SUBTITLES"




