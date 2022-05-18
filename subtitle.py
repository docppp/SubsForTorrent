import logging
import re

import utilities


class Subtitle:
    def __init__(self, name, subtitle_id):
        self.name = name
        self.subtitle_id = subtitle_id
        self.address = f"https://www.opensubtitles.org/pl/subtitles/{subtitle_id}"
        self.page = utilities.get_page(self.address)
        self.fps = self.get_subtitle_fps()
        self.link = self.get_subtitle_link()

    def get_subtitle_fps(self):
        r = re.search('[0-9]+.[0-9]* FPS\n', self.page.text)
        if r:
            return float(r.group(0)[:-4])
        return 0

    def get_subtitle_link(self):
        r = re.search('http://dl.opensubtitles.org/.*/download/file/[0-9]*', self.page.text)
        if r:
            return r.group(0)
        logging.error(f"Could not find download link at {self.address}")

    def __str__(self):
        num_of_spaces = int((64 - len(self.name)))
        num_of_spaces = 1 if num_of_spaces < 1 else num_of_spaces
        spaces = ' ' * num_of_spaces
        return f"Subtitle: {self.name}{spaces}FPS: {self.fps:6.3f}\tlink: {self.link}"

