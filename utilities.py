import logging
from collections import defaultdict
from pathlib import Path

import PTN
import requests
from videoprops import get_video_properties


class MovieError(LookupError):
    pass


class SubtitleError(LookupError):
    pass


def fps_from_frame_rate(frame_rate: str):
    return {
        '24000/1001':   23.976,
        '25/1':         25,
        '30000/1001':   29.97
    }[frame_rate]


def get_file_mediainfo(file_path: Path):
    info = PTN.parse(file_path.name)
    file_props = get_video_properties(str(file_path))
    info['fps'] = fps_from_frame_rate(file_props['r_frame_rate'])
    return info


def get_page(address: str):
    logging.info(f"GET: {address}")
    return requests.get(address)


def damerau_levenshtein(s1, s2):
    def _check_type(s):
        if not isinstance(s, str):
            raise TypeError("expected str or unicode, got %s" % type(s).__name__)

    _check_type(s1)
    _check_type(s2)

    len1 = len(s1)
    len2 = len(s2)
    infinite = len1 + len2

    # character array
    da = defaultdict(int)

    # distance matrix
    score = [[0] * (len2 + 2) for x in range(len1 + 2)]

    score[0][0] = infinite
    for i in range(0, len1 + 1):
        score[i + 1][0] = infinite
        score[i + 1][1] = i
    for i in range(0, len2 + 1):
        score[0][i + 1] = infinite
        score[1][i + 1] = i

    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            i1 = da[s2[j - 1]]
            j1 = db
            cost = 1
            if s1[i - 1] == s2[j - 1]:
                cost = 0
                db = j

            score[i + 1][j + 1] = min(
                score[i][j] + cost,
                score[i + 1][j] + 1,
                score[i][j + 1] + 1,
                score[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1),
            )
        da[s1[i - 1]] = i

    return score[len1 + 1][len2 + 1]
