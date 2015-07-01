from sys import stderr
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.stem import SnowballStemmer
import enchant
import re


MESSAGE_EVERY = 10000

class ArxivCleaner(object) :
    def __init__(self) :
        self.latex_pattern = re.compile("\\\\(?:begin|end)\\{[^\\}]+\\}|\\\\[^$\\{\s]+[$\\{\s]")
        self.badchars_pattern = re.compile("[^a-zA-Z\s]")
        
        self.wiki_match_badchars = re.compile("[^A-Za-z0-9_\,\.\(\)\-\s]")
        self.wiki_sub_remove = re.compile("[\"\(\)\,:]")
        self.wiki_sub_replace = re.compile("[\-_/]")

        self.enchant_dict_us = enchant.Dict('en_US')
        self.enchant_dict_gb = enchant.Dict('en_GB')

        self.science_dict = self.build_custom_dict()
        self.stemmer = SnowballStemmer('english')

    def build_custom_dict(self) :
        science_dict = set()

        # wikipedia titles contain all kinds of weird characters
        # at the beginning and end of lines, filter these ones out...
        for wordlist in ('custom_scientific_US_ascii.txt', 'custom_scientific_UK_ascii.txt', 'wiktionary_english_only.txt') :
            with open(wordlist) as f :
                for line in f :
                    line = line.strip()

                    if line[0] in ".(!&'*+-/0123456789@?=;\"" :
                        continue

                    line = self.wiki_sub_remove.sub('', line)
                    line = self.wiki_sub_replace.sub(' ', line)

                    for i in line.strip().split() :
                        if i.upper() == i :
                            continue

                        if not self.badchars_pattern.search(i) :
                            science_dict.add(i.lower())

            print >> stderr, "added %s, %d words in dict" % (wordlist, len(science_dict))

        return science_dict

    def contains_latex(self, s) :
        return self.latex_pattern.search(s)

    def tokens_remove_nonenglish(self, tokens) :
        return [ t for t in tokens if self.enchant_dict_us.check(t) or self.enchant_dict_gb.check(t) or t in self.science_dict ]

    def string_remove_latex(self, s) :
        return self.latex_pattern.sub(' ', s)

    def string_tokenize(self, s) :
        return s.split()

    def tokens_stringize(self, tokens) :
        return " ".join(tokens)

    def tokens_stem(self, tokens) :
        return [ self.stemmer.stem(t) for t in tokens ]

    def string_preprocess(self, s) :
        return s.replace('\n', ' ')

    def string_remove_punctuation(self, s) :
        return self.badchars_pattern.sub(' ', s)

    def get_good_words(s) :
        return self.tokens_remove_nonenglish(
                 self.string_tokenize(
                   self.string_remove_punctuation(
                     self.string_preprocess(s))))

    def clean_string(self, s, wordlist) :
        return self.tokens_stringize(
                 self.tokens_remove_nonwordlist(wordlist,
                   self.string_tokenize( 
                     self.string_remove_punctuation(
                       self.string_remove_latex(
                         self.string_preprocess(s))).lower())))

    def clean_string_stem(self, s, wordlist) :
        return self.tokens_stringize(
                 self.tokens_stem(
                    self.tokens_remove_nonwordlist(wordlist,
                      self.string_tokenize( 
                        self.string_remove_punctuation(
                          self.string_remove_latex(
                            self.string_preprocess(s))).lower()))))

    def build_wordlist(self, articles) :
        wordlist = set()
        num_articles = len(articles)

        # build a word list based on articles without any latex
        for index,a in enumerate(articles) :
            s = a.title + ' ' + a.abstract

            if self.contains_latex(s) :
                continue

            for word in self.get_good_words(s) :
                wordlist.add(word.lower())

            if (index % MESSAGE_EVERY) == 0 :
                print >> stderr, "building wordlist %d/%d articles" % (index, num_articles)           

        return wordlist

    def build_corpus(self, articles, stem=True) :
        num_articles = len(articles)
        wordlist = self.build_wordlist(articles)
        corpus = []

        for index,a in enumerate(articles) :
            s = a.title + ' ' + a.abstract

            if stem :
                corpus.append(self.clean_string_stem(s, wordlist))
            else :
                corpus.append(self.clean_string(s, wordlist))

            if (index % MESSAGE_EVERY) == 0 :
                print >> stderr, "preprocessing %d/%d articles" % (index, num_articles)

        return corpus

