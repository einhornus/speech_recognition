import nltk
from nltk.corpus import brown
from nltk.util import ngrams
nltk.download()
# Access the corpus
corpus = nltk.corpus.udhr_rus.words()

# Generate trigrams
trigrams = ngrams(corpus, 3)

# Frequency Distribution
fdist = nltk.FreqDist(trigrams)

# Find the relative probability of a certain trigram
trigram = ("just", "like", "that")
relative_prob = fdist.freq(trigram)
print(relative_prob)