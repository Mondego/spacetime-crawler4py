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
    try:
        with open(text_file_path, 'r', encoding='UTF-8') as all_values:
            read_text = all_values.read(chunk_size).lower()
            input_text = read_text
            while read_text:
                last_space = input_text.rfind(' ')
                extra_text = input_text[last_space + 1:]
                main_text = ('' if last_space == -1 else input_text[:last_space])

                token_list += re.findall(regex, main_text)
                read_text = all_values.read(chunk_size).lower()
                input_text = extra_text + read_text
                if read_text == '':
                    token_list += re.findall(regex, input_text)
        return token_list
    except FileNotFoundError:
        assert False, f"Error: File\n" \
                      f"{text_file_path}\n" \
                      f" was not found."
    except UnicodeDecodeError:
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