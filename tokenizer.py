import re
from collections import defaultdict


def tokenize(text_string, only_relevant_words=False) -> [str]:
    # this is the list of all the tokens
    token_list = []
    # this is the regex which searches for valid strings
    # the valid strings can contain letters, numbers, or both
    regex = '[a-z0-9]+'
    # this is the size of the chunks which are taken into
    # memory at a time
    chunk_size = 1024
    # This lists all the irrelevant words.
    apostrophe_stopwords = set()
    stopwords = set()
    if only_relevant_words:
        apostrophe_stopwords = {"aren't", "can't", "couldn't", "didn't", "doesn't", "don't", "hadn't", "hasn't",
                                 "haven't", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've",
                                 "isn't", "it's", "let's", "mustn't", "shan't", "she'd", "she'll", "she's", "shouldn't",
                                 "that's", "there's", "they'd", "they'll", "they're", "they've", "wasn't", "we'd",
                                 "we'll", "we're", "we've", "weren't", "what's", "when's", "where's", "who's", "why's",
                                 "won't", "wouldn't", "you'd", "you'll", "you're", "you've"}
        stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as',
                      'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
                      'cannot', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
                      'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
                      'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'me', 'more',
                      'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
                      'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some',
                      'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
                      'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
                      'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you',
                      'your', 'yours', 'yourself', 'yourselves'}
    try:
        with open(text_string, 'r', encoding='UTF-8') as all_values:
            read_text = all_values.read(chunk_size).lower()
            # This is where the text to be read will go in general.
            input_text = read_text
            while read_text:
                # These variables exist in case the end of the bytes is in the middle of a word.
                last_space = input_text.rfind(' ')
                extra_text = input_text[last_space + 1:]

                # This is the part of the text which consists of whole words
                main_text = ('' if last_space == -1 else input_text[:last_space])

                # This takes out the stop words which specifically have apostrophes in them
                # because otherwise it would also take out non stop-words like won and don
                # which appear in won't and don't, and other problems could arise from that.
                for word in apostrophe_stopwords:
                    main_text = re.sub(word, '', main_text)

                # This finds all the words in main_text
                # which are not in the remaining stop words.
                token_list += [token for token in re.findall(regex, main_text) if token not in stopwords]
                read_text = all_values.read(chunk_size).lower()

                # The part of the text which doesn't necessarily consist of whole words
                # is added to the beginning to be parsed again.
                input_text = extra_text + read_text
                if read_text == '':
                    token_list += [token for token in re.findall(regex, input_text) if token not in stopwords]
        return token_list
    except UnicodeDecodeError:
        # This is what happens when you put a .jpg or something into this code.
        assert False, f'Error: File\n' \
                      f'{text_string}\n' \
                      f'is not considered a text file by this code\n' \
                      f'because it cannot be encoded into UTF-8.'


def compute_word_frequencies(token_list: [str]) -> {str: int}:
    frequencies = defaultdict(int)
    for token in token_list:
        frequencies[token] += 1
    return frequencies


def token_print(frequencies: {str: int}):
    double_sorted = sorted(sorted(frequencies.items(), key=(lambda x: x[0])), key=(lambda x: x[1]), reverse=True)
    for key, value in double_sorted[:50]:
        print(key, value, sep=' - ')


if __name__ == '__main__':
    token_print(compute_word_frequencies(tokenize('README.md', True)))
