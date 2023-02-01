"""
import os
os.chdir("..//..//src")
print(os.getcwd())
"""

import torch
import transformers
import itertools
import numpy as np
import src.nlp_manager_module.nlp_manager
from collections import defaultdict
import torch.nn


class Aligner:
    def __init__(self, manager):
        can_use_small = True
        small_langs = ['ar', 'de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'nl', 'pl', 'pt', 'ru', 'th', 'tr', 'zh']
        for lang in manager.dictionaries:
            if not (lang in small_langs):
                can_use_small = False
        print("can_use_small:", can_use_small)
        if not can_use_small:
            self.model = transformers.BertModel.from_pretrained('setu4993/LaBSE', cache_dir="models")
            self.tokenizer = transformers.BertTokenizer.from_pretrained('setu4993/LaBSE', cache_dir="models")
        else:
            self.model = transformers.BertModel.from_pretrained('setu4993/smaller-LaBSE', cache_dir="models")
            self.tokenizer = transformers.BertTokenizer.from_pretrained('setu4993/smaller-LaBSE', cache_dir="models")

        self.model.eval()
        self.manager = manager

    def align(self, s1, lang1, s2, lang2):
        """
        if not lang1 in self.dictionaries:
            self.dictionaries[lang1] = src.nlp_manager_module.dictionary.Dictionary(lang1)
        if not lang2 in self.dictionaries:
            self.dictionaries[lang2] = src.nlp_manager_module.dictionary.Dictionary(lang2)
        converted1 = self.dictionaries[lang1].convert(s1, {})
        converted2 = self.dictionaries[lang2].convert(s2, {})
        """

        converted1 = self.manager.raw_convert(s1, lang1, {})
        converted2 = self.manager.raw_convert(s2, lang2, {})
        aligned = self._align(converted1, converted2)
        return aligned

    def _align(self, conversion1, conversion2, antiglue=0.0, cosine_k=-1, power_k1=0.2, power_k2=0.05):
        cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)

        if len(conversion1) == 0 or len(conversion2) == 0:
            return [], conversion1, conversion2

        if not ('raw_token' in conversion1[0]):
            c1 = conversion1
            c2 = conversion2
            for i in range(len(c1)):
                c1[i] = {'raw_token': c1[i], 'token': c1[i]}
            for i in range(len(c2)):
                c2[i] = {'raw_token': c2[i], 'token': c2[i]}
            conversion1 = c1
            conversion2 = c2

        tokenizer = self.tokenizer
        model = self.model

        sent_src = []
        sent_tgt = []
        for i in range(len(conversion1)):
            sent_src.append(conversion1[i]["raw_token"])
        for i in range(len(conversion2)):
            sent_tgt.append(conversion2[i]["raw_token"])

        token_src, token_tgt = [tokenizer.tokenize(word) for word in sent_src], [tokenizer.tokenize(word) for word in
                                                                                 sent_tgt]
        wid_src, wid_tgt = [tokenizer.convert_tokens_to_ids(x) for x in token_src], [tokenizer.convert_tokens_to_ids(x)
                                                                                     for x in
                                                                                     token_tgt]
        ids_src, ids_tgt = tokenizer.prepare_for_model(list(itertools.chain(*wid_src)), return_tensors='pt',
                                                       model_max_length=tokenizer.model_max_length, truncation=True)[
            'input_ids'], \
            tokenizer.prepare_for_model(list(itertools.chain(*wid_tgt)), return_tensors='pt',
                                        truncation=True,
                                        model_max_length=tokenizer.model_max_length)['input_ids']
        sub2word_map_src = []
        for i, word_list in enumerate(token_src):
            sub2word_map_src += [i for x in word_list]
        sub2word_map_tgt = []
        for i, word_list in enumerate(token_tgt):
            sub2word_map_tgt += [i for x in word_list]

        align_layer = 8
        with torch.no_grad():
            us1 = ids_src.unsqueeze(0)
            us2 = ids_tgt.unsqueeze(0)
            m1 = model(us1, output_hidden_states=True)
            m2 = model(us2, output_hidden_states=True)
            r1 = m1[2]
            r2 = m2[2]
            out_src = r1[align_layer][0, 1:-1]
            out_tgt = r2[align_layer][0, 1:-1]
            # dot_prod = torch.matmul(out_src, out_tgt.transpose(-1, -2))

            if cosine_k != -1:
                sz1 = list(out_src.size())
                sz2 = list(out_tgt.size())

                cosines = torch.zeros([sz1[0], sz2[0]], dtype=torch.float32)
                for i in range(sz1[0]):
                    for j in range(sz2[0]):
                        arg1 = out_src[i]
                        arg2 = out_tgt[j]
                        cossim = cos(arg1, arg2) * cosine_k
                        cosines[i][j] = cossim

                softmax_srctgt = torch.nn.Softmax(dim=-1)(cosines)
                softmax_tgtsrc = torch.nn.Softmax(dim=-2)(cosines)
            else:
                dot_prod = torch.matmul(out_src, out_tgt.transpose(-1, -2))
                softmax_srctgt = torch.nn.Softmax(dim=-1)(dot_prod)
                softmax_tgtsrc = torch.nn.Softmax(dim=-2)(dot_prod)

        res = []
        res = defaultdict(list)

        connections_from = [[[] for j in range(len(conversion2))] for i in range(len(conversion1))]
        connections_to = [[[] for j in range(len(conversion1))] for i in range(len(conversion2))]

        connections = defaultdict(list)

        for i in range(softmax_srctgt.shape[0]):
            id1 = sub2word_map_src[i]
            for j in range(softmax_srctgt.shape[1]):
                id2 = sub2word_map_tgt[j]

                connections_from[id1][id2].append(softmax_srctgt[i][j].item())
                connections_to[id2][id1].append(softmax_tgtsrc[i][j].item())

                key1 = {'from': conversion1[id1]['raw_token'], 'to': conversion2[id2]['raw_token'], 'dicrection': True,
                        'id1': id1, 'id2': id2}
                key2 = {'from': conversion2[id2]['raw_token'], 'to': conversion1[id1]['raw_token'], 'dicrection': False,
                        'id1': id1, 'id2': id2}

                connections[frozenset(key1.items())].append(softmax_srctgt[i][j].item())
                connections[frozenset(key1.items())].append(softmax_tgtsrc[i][j].item())

        pairs = []
        for key in connections:
            ar = connections[key]
            avg = sum(ar) / len(ar)
            mx = max(ar)
            real = mx * avg
            pairs.append([key, real])
        pairs.sort(key=lambda x: -x[1])

        # connections.sort(key=lambda x:-x['strength'])

        res = []

        # sets = {}
        matched_indexes = set()
        total_to_match = len(conversion1)

        for i in range(len(pairs)):
            power = pairs[i][1]

            matched = len(matched_indexes)
            percentage_matched = matched / total_to_match

            POWER_LIMIT = power_k1 * (1.0 - percentage_matched) + power_k2 * percentage_matched

            # print(matched, total_to_match, POWER_LIMIT)

            if power < POWER_LIMIT:
                break

            id1 = dict(pairs[i][0])['id1']
            id2 = dict(pairs[i][0])['id2']

            indexes = []
            for j in range(len(res)):
                if id1 in res[j][0] or id2 in res[j][1]:
                    indexes.append(j)

            existing_sum = 0
            for j in range(len(indexes)):
                for jj in range(len(res[j][2])):
                    existing_sum += res[j][2][jj][2]
            new_sum = existing_sum + power
            if power < new_sum * antiglue:
                indexes = None

            if not (indexes is None):
                all1 = set()
                all2 = set()
                for j in range(len(indexes)):
                    for q in res[indexes[j]][0]:
                        all1.add(q)
                    for q in res[indexes[j]][1]:
                        all2.add(q)
                all1.add(id1)
                all2.add(id2)
                all1 = sorted(list(all1))
                all2 = sorted(list(all2))

                for j in range(len(all1) - 1):
                    if all1[j + 1] > all1[j] + 1:
                        for jj in range(all1[j] + 1, all1[j + 1]):
                            if "is_punctuation" in conversion1[jj]:
                                if not (conversion1[jj]["is_punctuation"]):
                                    indexes = None
                                    break
                            else:
                                indexes = None

                """
                for j in range(len(all2) - 1):
                    if all2[j + 1] > all2[j] + 1:
                        for jj in range(all2[j] + 1, all2[j+1]):
                            if "is_punctuation" in conversion2[jj]:
                                if not (conversion2[jj]["is_punctuation"]):
                                    #indexes = None
                                    break
                            else:
                                indexes = None
                """

            if not (indexes is None):
                if len(indexes) == 0:
                    s1 = set()
                    s2 = set()
                    s1.add(id1)
                    s2.add(id2)
                    res.append((s1, s2, [(id1, id2, power)]))
                    matched_indexes.add(id1)
                else:
                    for j in range(1, len(indexes)):
                        for q in res[indexes[j]][0]:
                            res[indexes[0]][0].add(q)
                        for q in res[indexes[j]][1]:
                            res[indexes[0]][1].add(q)
                        for q in res[indexes[j]][2]:
                            res[indexes[0]][2].append(q)
                        res[indexes[j]] = (set(), set(), [])
                    res[indexes[0]][0].add(id1)
                    res[indexes[0]][1].add(id2)
                    res[indexes[0]][2].append((id1, id2, power))
                    matched_indexes.add(id1)

        newres = []
        for i in range(len(res)):
            if len(res[i][0]) == 0 and len(res[i][1]) == 0:
                pass
            else:
                newres.append(res[i])

        return newres, conversion1, conversion2


if __name__ == "__main__":
    manager = src.nlp_manager_module.nlp_manager.NLPManager(['fr', 'en'])
    aligner = Aligner(manager)

    # s1 = 'Un sac d \'or si vous réussissez'.split(' ')
    # s2 = 'A bag of gold if you succeed'.split(' ')

    s1 = "Marie va te donner une chance supplémentaire."
    s2 = "Mary is going to give you another chance."

    l1 = 'fr'
    l2 = 'en'
    res, c1, c2 = aligner.align(s1, l1, s2, l2)
    # res, c1, c2 = aligner._align(s1, s2, antiglue=0.25)

    for i in range(len(res)):
        s1 = sorted(list(res[i][0]))
        s2 = sorted(list(res[i][1]))

        str1 = ""
        str2 = ""

        for j in s1:
            str1 += c1[j]["raw_token"] + " "

        for j in s2:
            str2 += c2[j]["raw_token"] + " "

        print(str1, " === ", str2)
    print(res)
