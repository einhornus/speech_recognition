import src.translation.DeepLTranslator


if __name__ == "__main__":
    t = src.translation.DeepLTranslator.DeepLTranslator()
    res = t.translate('I love you', 'en', 'ru')
    print(res)






#https://www.netflix.com/watch/80134330