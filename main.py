import logging
from pathlib import Path

from gooey import Gooey, GooeyParser

import utilities
from downloader import Downloader


@Gooey(monospace_display=True,
       default_size=(800, 550))
def main():
    logging.basicConfig(format='[%(levelname)s] %(module)s:\t%(message)s', level=logging.INFO)
    logging.addLevelName(logging.DEBUG, 'DBG')
    logging.addLevelName(logging.INFO, 'INF')
    logging.addLevelName(logging.WARNING, 'WRN')
    logging.addLevelName(logging.ERROR, 'ERR')

    parser = GooeyParser()
    parser.add_argument('filename', type=str, help="Path to movie file to process", widget="FileChooser")
    parser.add_argument('--no-rename', action='store_true', help="Do not rename subtitle file to match movie file")
    parser.add_argument('--no-override', action='store_true', help="Do not override existing file")
    parser.add_argument("--unknown-fps", action='store_true', help="Allow subtitles with not specified fps rate")
    args = parser.parse_args()

    try:
        d = Downloader(Path(args.filename),
                       rename_sub=not args.no_rename,
                       override_files=not args.no_override,
                       allow_unknown_fps=args.unknown_fps)
        d.download_subtitles()
        # TODO:
        # download subs in whole directory at once
    except utilities.MovieError:
        pass
    except utilities.SubtitleError:
        pass


if __name__ == '__main__':
    main()


# pyinstaller -F -w --collect-binaries videoprops main.py
