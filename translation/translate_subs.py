import copy


def group_by_time(subs, limit, limit2=15):
    groups = [[subs.data[0]]]
    for i in range(1, len(subs.data)):
        dist = subs.data[i]["from"] - subs.data[i - 1]["to"]
        if dist > limit or len(groups[-1]) > limit2:
            groups.append([subs.data[i]])
        else:
            groups[len(groups) - 1].append(subs.data[i])
    return groups


def just_translate(translator, srt, from_, to_):
    newsrt = []
    grouped = group_by_time(srt, -1)

    all_contents = []
    for i in range(len(grouped)):
        content = ""
        for j in range(len(grouped[i])):
            content += grouped[i][j]["text"].replace("\n", " ")
            content += "\n"
        all_contents.append(content)
    translator.translate(all_contents, from_, to_)

    for i in range(len(grouped)):
        content = ""
        for j in range(len(grouped[i])):
            content += grouped[i][j]["text"].replace("\n", " ")
            content += "\n"
        res = translator.translate(content, from_, to_)
        splitted = res.split("\n")

        if len(grouped[i]) != len(res.split("\n")) - 1:
            # print('error', len(grouped[i]), len(res.split("\n")))
            for j in range(len(grouped[i])):
                newtext = translator.translate(grouped[i][j]["text"].replace("\n", " "), from_, to_)
                sss = copy.deepcopy(grouped[i][j])
                sss["text"] = newtext
                sss["text"] = sss["text"].replace("\r", "")
                newsrt.append(sss)
        else:
            spllited_translations = res.split("\n")
            for j in range(len(spllited_translations) - 1):
                sss = copy.deepcopy(grouped[i][j])
                sss["text"] = spllited_translations[j]
                sss["text"] = sss["text"].replace("\r", "")
                newsrt.append(sss)

    return newsrt

