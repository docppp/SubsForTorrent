import logging
from pathlib import Path

import PTN

import utilities
from subtitle import Subtitle


class Matcher:

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_info = utilities.get_file_mediainfo(file_path)
        logging.info(f"FOUND: {self.file_info}")

    def get_best_subtitles(self, subtitles: list[Subtitle], allow_unknown_fps: bool):
        scores = [self.get_subtitle_matching_score(s) for s in subtitles]
        min_score = 0 if allow_unknown_fps else 1
        filtered = filter(lambda s: s >= min_score, scores)
        scores = list(filtered)
        if len(scores) == 0:
            logging.error("NOT FOUND: No matching subtitles, allow unknown fps for better results")
            raise utilities.SubtitleError
        return subtitles[scores.index(max(scores))]

    def get_subtitle_matching_score(self, sub: Subtitle):
        if sub.fps == 0:
            logging.info(f"SCORE: {0} for {sub.name}")
            return 0

        if sub.fps != self.file_info['fps']:
            logging.info(f"SCORE: {-1} for {sub.name}")
            return -1

        sub_info = PTN.parse(sub.name)

        def check_similarity(key):
            try:
                return sub_info[key].lower() == self.file_info[key].lower()
            except KeyError:
                return False

        score = 1
        score += check_similarity('group') * 3
        score += check_similarity('quality') * 2
        score += check_similarity('codec') * 1
        logging.info(f"SCORE: {score} for {sub.name}")
        return score




