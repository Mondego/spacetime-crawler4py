import re
from collections import defaultdict


# This is O(N).
# The function .lower() goes through the entire text chunk by chunk
# in a linear fashion, which is O(N).
# The while loop goes through the entire text chunk-by-chunk and is therefore O(N).
# The function .rfind(' ') is O(chunk_size) in the worst case where there is no space.
# The code input_text[:last_space] is O(N) in the case where the space is the very last
# character.
# The regex is [a-zA-Z0-9]+ which only involves one character at most to be
# fulfilled and so no backtracking happens, meaning the worst-case is O(N).
def tokenize(text_file_path) -> [str]:
    # this is the list of all the tokens
    token_list = []
    # this is the regex which searches for valid strings
    # the valid strings can contain letters, numbers, or both
    regex = '[a-z0-9]+'
    # this is the size of the chunks which are taken into
    # memory at a time
    chunk_size = 1024
    # These are all the stop words that I feel are relevant.
    # '''This is here to test how it works with no stop words.
    stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren',
                 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can',
                 'cannot', 'could', 'couldn', 'd', 'did', 'didn', 'do', 'does', 'doesn', 'doing', 'don', 'down',
                 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', 'has', 'hasn', 'have', 'haven',
                 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
                 'into', 'is', 'isn', 'it', 'its', 'itself', 'let', 'll', 'm', 'me', 'more', 'most', 'mustn', 'my',
                 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours',
                 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', 'she', 'should', 'shouldn', 'so', 'some',
                 'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
                 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn',
                 'we', 'were', 'weren', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'won',
                 'would', 'wouldn', 'you', 'your', 'yours', 'yourself', 'yourselves'}

    '''# This is here to test how it works with no stop words.
    stopwords = {}
    # '''
    try:
        with open(text_file_path, 'r', encoding='UTF-8') as all_values:
            read_text = all_values.read(chunk_size).lower()
            # This is where the text to be read will go in general.
            input_text = read_text
            while read_text:
                # These variables exist in case the end of the bytes is in the middle of a word.
                last_space = input_text.rfind(' ')
                extra_text = input_text[last_space + 1:]

                # This is the part of the text which consists of whole words
                main_text = ('' if last_space == -1 else input_text[:last_space])

                # This finds all the words in main_text.
                token_list += [token for token in re.findall(regex, main_text) if token not in stopwords]
                read_text = all_values.read(chunk_size).lower()
                # The part of the text which doesn't necessarily consist of whole words
                # is added to the beginning to be parsed again.
                input_text = extra_text + read_text
                if read_text == '':
                    token_list += re.findall(regex, input_text)
        return token_list
    except FileNotFoundError:
        # This is what happens when the file can't be found.
        assert False, f"Error: File\n" \
                      f"{text_file_path}\n" \
                      f" was not found."
    except UnicodeDecodeError:
        # This is what happens when you put a .jpg or something into this code.
        assert False, f'Error: File\n' \
                      f'{text_file_path}\n' \
                      f'is not considered a text file by this code\n' \
                      f'because it cannot be encoded into UTF-8.'


# This is O(N).
# The number of times a change in number occurs increases
# linearly (O(N)) with the number of tokens in token_list.
def compute_word_frequencies(token_list: [str]) -> {str: int}:
    frequencies = defaultdict(int)
    for token in token_list:
        frequencies[token] += 1
    return frequencies


if __name__ == '__main__':
    for key, value in sorted(compute_word_frequencies(tokenize('README.md')).items(),
                             key=(lambda x: x[1])):
        print(f'{key}: {value}')
