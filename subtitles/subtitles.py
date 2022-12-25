import subtitles.utils


class Subtitles:
    def __init__(self, **args):
        if "file" in args:
            self.data = subtitles.utils.get_subs(args["file"])
        else:
            self.data = []

    def save(self, file_name):
        subtitles.utils.drop(self.data, file_name)