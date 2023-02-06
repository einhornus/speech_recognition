import copy


def group_by_sentences(subs):
    groups = []
    current_group = []
    for i in range(0, len(subs.data)):
        if len(current_group) > 0 and len(current_group[-1]["text"]) > 0 and current_group[-1]["text"][-1] in [".", "!",                                                                                                    "?"]:
            groups.append(current_group)
            current_group = [subs.data[i]]
        else:
            current_group.append(subs.data[i])

    groups.append(current_group)
    return groups


def just_translate(translator, srt, from_, to_):
    delimiter = " + "

    newsrt = []
    grouped = group_by_sentences(srt)

    succes = 0
    fail = 0

    for i in range(len(grouped)):
        content = ""
        for j in range(len(grouped[i])):
            content += grouped[i][j]["text"]
            if j != len(grouped[i]) - 1:
                content += delimiter
        translation = translator.translate(content, from_, to_, db_path=None)
        translation_content = translation.split(delimiter)
        if len(translation_content) != len(grouped[i]):
            fail += 1
            for j in range(len(grouped[i])):
                translation = translator.translate(grouped[i][j]["text"], from_, to_, db_path=None)
                newsrt.append({
                    "from": grouped[i][j]["from"],
                    "to": grouped[i][j]["to"],
                    "text": translation
                })
        else:
            succes += 1
            for j in range(len(translation_content)):
                newsrt.append(
                    {
                        "from": grouped[i][j]["from"],
                        "to": grouped[i][j]["to"],
                        "text": translation_content[j]
                    }
                )
        print(f"Translated {i + 1}/{len(grouped)} groups. Success: {succes}, Fail: {fail}")
    return newsrt
