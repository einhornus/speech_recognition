import subtitles.subs

def align(file_original, file_translation):
    subs_original = subtitles.subs.Subtitles(file=file_original).data
    subs_translation = subtitles.subs.Subtitles(file=file_translation).data

    sizes_original = []
    sizes_translation = []
    for i in range(len(subs_original)):
        sizes_original.append(subs_original[i]["to"] - subs_original[i]["from"])
    for i in range(len(subs_translation)):
        sizes_translation.append(subs_translation[i]["to"] - subs_translation[i]["from"])
    begins_original = []
    begins_translation = []
    for i in range(len(subs_original)):
        begins_original.append(subs_original[i]["from"])
    for i in range(len(subs_translation)):
        begins_translation.append(subs_translation[i]["from"])
    ends_original = []
    ends_translation = []
    for i in range(len(subs_original)):
        ends_original.append(subs_original[i]["to"])
    for i in range(len(subs_translation)):
        ends_translation.append(subs_translation[i]["to"])

    absolute_diff_limit = 500

    while True:
        for i in range(len(subs_original)):
            for j in range(len(subs_translation)):
                diff = abs(sizes_original[i] - sizes_translation[j])
                if diff < absolute_diff_limit:
                    midpoint = (subs_original[i]["from"] + subs_original[i]["to"]) / 2
                    move_original_me = diff / 2
                    move_original_neighbor = 0
                    move_translation_me = diff / 2
                    move_translation_neighbor = 0



if __name__ == "__main__":
    align("data//youtube//MyMT4DR8-PM_og.srt", "data//youtube//MyMT4DR8-PM_en.srt")