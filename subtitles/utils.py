def parse_time(time):
    parts = time.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    sm = parts[2].split(',')
    seconds = int(sm[0])
    ms = int(sm[1])
    res = ms + seconds * 1000 + minutes * 60 * 1000 + hours * 60 * 60 * 1000
    return res


def make_time(time):
    res = ""
    hours = time // (3600 * 1000)
    minutes = (time - 3600 * 1000 * hours) // (60 * 1000)
    seconds = (time - 3600 * 1000 * hours - 60 * 1000 * minutes) // (1000)
    milliseconds = time % 1000

    s1 = str(hours)
    s2 = str(minutes)
    s3 = str(seconds)
    s4 = str(milliseconds)

    if len(s1) == 1:
        s1 = "0" + s1

    if len(s2) == 1:
        s2 = "0" + s2

    if len(s3) == 1:
        s3 = "0" + s3

    if len(s4) == 1:
        s4 = "00" + s4

    if len(s4) == 2:
        s4 = "0" + s4

    res = s1 + ":" + s2 + ":" + s3 + "," + s4
    return res


def remove_tags(str):
    res = ""
    balance = 0

    for i in range(len(str)):
        if str[i] == '<':
            balance += 1

        if str[i] == '>':
            balance -= 1

        if balance == 0 and str[i] != '<' and str[i] != '>':
            res += str[i]
    return res


def group_by_time(subs, limit, limit2=15):
    groups = [[subs[0]]]
    for i in range(1, len(subs)):
        dist = subs[i]["from"] - subs[i - 1]["to"]
        if dist > limit or len(groups[-1]) > limit2:
            groups.append([subs[i]])
        else:
            groups[len(groups) - 1].append(subs[i])
    return groups


def get_subs(path):
    #with open("..//data//subtitles//" + path, mode='r', encoding='utf-8') as f:
    with open(path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
    return parse_subtitles(lines)


def parse_subtitles(data):
    groups = []
    last_group = []

    for i in range(len(data)):
        data[i] = data[i].replace("\r", "")
        data[i] = data[i].replace("\n", "")
        data[i] = data[i].replace("-->", "--[]")
        data[i] = remove_tags(data[i])

        if data[i] == '':
            if len(last_group) >= 2:
                groups.append(last_group)
            last_group = []
        else:
            last_group.append(data[i])

    if len(last_group) > 2:
        groups.append(last_group)

    res = []
    for i in range(len(groups)):
        time = groups[i][1]
        time_split = time.split(' --[] ')
        try:
            from_time = parse_time(time_split[0])
            to_time = parse_time(time_split[1])
            subs = ""
            for j in range(2, len(groups[i])):
                subs += groups[i][j]
                if j != len(groups[i]) - 1:
                    subs += '\n'
            res.append({"from": from_time, "to": to_time, "text": subs})
        except:
            print("ERROR:", groups[i])
    return res


def drop(srt_subs, file_name):
    res = ""
    for i in range(len(srt_subs)):
        res += str(i + 1) + "\n"
        t1 = make_time(srt_subs[i]["from"])
        t2 = make_time(srt_subs[i]["to"])
        res += t1 + " --> " + t2 + "\n"
        res += srt_subs[i]["text"] + "\n"
        res += "\n"

    with open(file_name, mode='w', encoding='utf-8') as f:
        f.write(res)
