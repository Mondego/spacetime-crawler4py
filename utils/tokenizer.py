import sys

STOPWORDS = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's",
    "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v", "w","x","y","z", "'"
]

def tokenize(readable_text):
    """
    Docstring for tokenize
    
    :param file_path: path of text file to tokenize
    Time Complexity: O(n) - Reads through text of file one time character by character
    """
    tokens = []
    token = ""

    try:
        for char in readable_text:
            if ('a' <= char.lower() <= 'z') or ('0' <= char <= '9') or char == "'":
                token += char.lower()
            else:
                if token:
                    if not token.isdigit():
                        tokens.append(token)
                    token = ""
        if token:
            tokens.append(token)
    except Exception:
        return []

    return tokens

def compute_word_frequencies(tokens_list):
    """
    Docstring for compute_word_frequencies
    
    :param tokens_list: list of tokens from tokenize()
    Time Complexity: O(n) - Iterates through tokens_list once
    """
    token_freqs = {}

    for token in tokens_list:
        if token in STOPWORDS:
            continue
        if token in token_freqs:
            token_freqs[token] += 1
        else:
            token_freqs[token] = 1

    return token_freqs

def print_tokens(token_freqs):
    """
    Docstring for print_tokens
    
    :param token_freqs: dictionary of tokens and their frequencies
    Time Complexity: O(nlogn) - Sorts the dictionary first and then iterates through 
    dictionary one time to print out each key/value pair
    """

    sorted_freqs = {token : freq for token, freq in sorted(token_freqs.items(), key=lambda item:item[1], reverse=True)}

    for token, freq in sorted_freqs.items():
        print(f"{token} - {freq}")

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("FORMAT: python program.py text_file")
#         sys.exit(1)

#     text_file = sys.argv[1]
#     tokens = tokenize(text_file)
#     token_frequencies = compute_word_frequencies(tokens)
#     print_tokens(token_frequencies)


# PART B

def count_matching_tokens(file1, file2):
    """
    Docstring for count_matching_tokens
    
    :param file1: first text file
    :param file2: second text file
    Time complexity: O(n + u)
        - tokenizes each file (O(n) + O(n) = O(n))
        - convert tokens list to set (O(u) where u is # of unique tokens)
    """
    tokens1 = set(tokenize(file1))
    tokens2 = set(tokenize(file2))
    matching = tokens1.intersection(tokens2)
    return len(matching)


# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("FORMAT: python program.py text_file1 text_file2")
#         sys.exit(1)

#     file1 = sys.argv[1]
#     file2 = sys.argv[2]
#     num_matching = count_matching_tokens(file1.strip(), file2.strip())
#     print(num_matching)