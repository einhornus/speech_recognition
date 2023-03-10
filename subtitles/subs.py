import subtitles.utils


class Subtitles:
    def __init__(self, **args):
        if "file" in args:
            self.data = subtitles.utils.get_subs(args["file"])
        else:
            self.data = []
        if "data" in args:
            self.data = args["data"]
        if "content" in args:
            self.data = subtitles.utils.get_subs_from_content(args["content"])

    def get_raw_content(self):
        res = ""
        for i in range(len(self.data)):
            res += self.data[i]["text"] + "\n"
        return res

    def get_content(self):
        return subtitles.utils.get_subs_content(self.data)

    @staticmethod
    def merge_subtitles(list):
        res = Subtitles()
        for i in range(len(list)):
            res.data.extend(list[i].data)
        res.data.sort(key=lambda x: x["from"])
        return res

    def get_average_logprob(self, r = None):
        if r is None:
            r = (0, len(self.data)-1)
        res = 0
        for i in range(r[0], r[1]+1):
            res += self.data[i]["logprob"]
        return res / (r[1] - r[0] + 1)

    def save(self, file_name):
        subtitles.utils.drop(self.data, file_name)