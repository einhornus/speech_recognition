import math

import subtitles.subs

NORMAL_SUB_LENGTH = 4000
DUAL_SUB_LENGTH = 10000


def split_text_into_parts(text, n):
    part_length = int(round(len(text) / n))
    start = 0
    parts = []
    for i in range(n):
        end = start + part_length
        parts.append(text[start:end])
        start = end
    # print(parts)

    for i in range(len(parts) - 1):
        p1 = parts[i]
        p2 = parts[i + 1]
        cost1 = 10000
        if " " in p1:
            cost1 = len(p1) - p1.rfind(" ")
        cost2 = 10000
        if " " in p2:
            cost2 = p2.find(" ")
        if cost1 == 10000 and cost2 == 10000:
            continue
        else:
            if cost1 < cost2:
                parts[i] = p1[:p1.rfind(" ")]
                parts[i + 1] = p1[p1.rfind(" "):] + p2
            else:
                parts[i] = p1 + p2[:p2.find(" ")]
                parts[i + 1] = p2[p2.find(" "):]
    return parts


def split_sub(item, max_duration):
    duration = item["to"] - item["from"]
    interval_count = math.ceil(duration / max_duration)
    interval_duration = duration / interval_count
    text_splits = split_text_into_parts(item["text"], interval_count)
    res = []
    for i in range(interval_count):
        res.append({
            "from": int(round(item["from"] + i * interval_duration)),
            "to": int(round(min(item["from"] + (i + 1) * interval_duration, item["to"]))),
            "text": text_splits[i]
        })
    return res


def split_subs_timely(subs, max_duration=NORMAL_SUB_LENGTH):
    res_data = []
    for i in range(len(subs.data)):
        if subs.data[i]["to"] - subs.data[i]["from"] <= max_duration:
            res_data.append(subs.data[i])
        else:
            res_data.extend(split_sub(subs.data[i], max_duration))
    res = subtitles.subs.Subtitles(data=res_data)
    return res


def merge_segments(list1, list2):
    res1 = []
    res2 = []

    start1 = 0
    start2 = 0
    end1 = 0
    end2 = 0
    while True:
        if end1 >= len(list1) or end2 >= len(list2):
            break

        if list1[end1]["to"] == list2[end2]["to"]:
            t1 = ""
            t2 = ""


            for i in range(start1, end1 + 1):
                if list1[i]["text"].startswith(" "):
                    list1[i]["text"] = list1[i]["text"][1:]

                if len(list1[i]["text"]) > 0 and list1[i]["text"][0].isupper() and t1.endswith(" "):
                    t1 += ". " + list1[i]["text"]
                else:
                    t1 += " " + list1[i]["text"]

            for i in range(start2, end2 + 1):
                if list2[i]["text"].startswith(" "):
                    list2[i]["text"] = list2[i]["text"][1:]

                if len(list2[i]["text"]) > 0 and list2[i]["text"][0].isupper() and t2.endswith(" "):
                    t2 += ". " + list2[i]["text"]
                else:
                    t2 += " " + list2[i]["text"]

            start = min(list1[start1]["from"], list2[start2]["from"])

            res1.append({
                "from": int(start),
                "to": int(list1[end1]["to"]),
                "text": t1
            })
            res2.append({
                "from": int(start),
                "to": int(list2[end2]["to"]),
                "text": t2
            })
            start1 = end1 + 1
            start2 = end2 + 1
            end1 = start1
            end2 = start2
        else:
            if list1[end1]["from"] < list2[end2]["from"]:
                end1 += 1
            else:
                end2 += 1
    for i in range(len(res1)):
        if res1[i]["from"] != res2[i]["from"] or res1[i]["to"] != res2[i]["to"]:
            print("ERROR: " + str(list1[i]) + " " + str(list2[i]))
    return res1, res2


def sync_subs(subs_original, subs_translation):
    subs_original = subs_original.data
    subs_translation = subs_translation.data

    sizes_original = []
    sizes_translation = []
    for i in range(len(subs_original)):
        sizes_original.append(subs_original[i]["to"] - subs_original[i]["from"])
    for i in range(len(subs_translation)):
        sizes_translation.append(subs_translation[i]["to"] - subs_translation[i]["from"])

    absolute_diff_limit = 500
    q = 0
    window_size = 3
    while q < 10000:
        diffs = []
        for i in range(len(subs_original)):
            central_index = int(round(i / len(subs_original) * len(subs_translation)))
            left_index = max(0, central_index - window_size)
            right_index = min(len(subs_translation) - 1, central_index + window_size + 1)
            for j in range(left_index, right_index):
                d_begin = abs(subs_original[i]["from"] - subs_translation[j]["from"])
                d_end = abs(subs_original[i]["to"] - subs_translation[j]["to"])
                if absolute_diff_limit >= d_begin > 0:
                    obj1 = {
                        "original": i,
                        "translation": j,
                        "diff": d_begin,
                        "type": "begin"
                    }
                    diffs.append(obj1)
                if absolute_diff_limit >= d_end > 0:
                    obj2 = {
                        "original": i,
                        "translation": j,
                        "diff": d_end,
                        "type": "end"
                    }
                    diffs.append(obj2)
        #diffs.sort(key=lambda x: x["diff"])
        if len(diffs) > 0:
            min_diff = diffs[0]
            for i in range(len(diffs)):
                if diffs[i]["diff"] < min_diff["diff"]:
                    min_diff = diffs[i]
            diff = min_diff
            if diff["type"] == "begin":
                midpoint = (subs_original[diff["original"]]["from"] + subs_translation[diff["translation"]]["from"]) / 2
                subs_original[diff["original"]]["from"] = midpoint
                subs_translation[diff["translation"]]["from"] = midpoint
            if diff["type"] == "end":
                midpoint = (subs_original[diff["original"]]["to"] + subs_translation[diff["translation"]]["to"]) / 2
                subs_original[diff["original"]]["to"] = midpoint
                subs_translation[diff["translation"]]["to"] = midpoint
        else:
            break
        q += 1

    #subs_original, subs_translation = merge_segments(subs_original, subs_translation)
    res1 = subtitles.subs.Subtitles(data=subs_original)
    res2 = subtitles.subs.Subtitles(data=subs_translation)

    #res1 = split_subs_timely(res1, DUAL_SUB_LENGTH)
    #res2 = split_subs_timely(res2, DUAL_SUB_LENGTH)
    return res1, res2


if __name__ == "__main__":
    subs_original = subtitles.subs.Subtitles(file="data//youtube//pb4YoMjcYM4_og.srt")
    subs_translation = subtitles.subs.Subtitles(file="data//youtube//pb4YoMjcYM4_en.srt")
    sync_subs(subs_original, subs_translation)
