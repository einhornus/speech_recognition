import storage.bert

MAX_RESULTS = 6

def search_catalogue(query, catalogue, original_language="an", language="og"):
    bert_query = None
    if query != "":
        bert_query = storage.bert.encode_bert(query)

    res = []
    words = query.split(" ")
    for video in catalogue.videos:
        if video.original_language == original_language or original_language == "an":
            if video.language == language or language == "an" or language == "og":
                if bert_query is None:
                    relevance = 0
                else:
                    relevance = storage.bert.sim(bert_query, video.content_embedding)
                print(video.title, relevance)
                res.append((video, relevance))
    res.sort(key=lambda x: x[1], reverse=True)

    result = []
    for i in range(len(res)):
        obj = {}
        obj["id"] = res[i][0].id
        obj["title"] = res[i][0].title
        obj["thumbnail"] = res[i][0].thumbnail
        result.append(obj)

    if len(result) > MAX_RESULTS:
        result = result[:MAX_RESULTS]

    return result