"""
Javon: Function left_rotate takes two parameters: x, 
which is the 32-bit integer to be rotated, and amount.
By shifting x to the left by amount bits and then OR-ing it 
with the result of shifting x to the right by (32 - amount) bits, 
the function achieves the left rotation.
"""
def left_rotate(x, amount):
    return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF

"""
Javon: Function md5_padding pads a message according to the MD5 algorithm before hashing. 
It appends a single '1' bit to the message followed by '0' bits until 
the length of the message is congruent to 448 modulo 512. Finally, 
it appends the original length of the message as a 64-bit little-endian 
integer, ensuring the message meets the required padding criteria for 
MD5 hashing.
"""
def md5_padding(message):
    original_length = len(message) * 8
    # Append a single '1' bit
    message += b'\x80'
    # Append '0' bits until the length is congruent to 448 mod 512
    while len(message) % 64 != 56:
        message += b'\x00'
    # Append the original length in bits as a 64-bit little-endian integer
    message += original_length.to_bytes(8, byteorder='little')
    return message

"""
Javon: Function md5 calculates the MD5 hash of a given string, initializes 
variables representing specific constants, then processes the message in 
512-bit chunks according to the MD5 algorithm, updating hash values iteratively. 
Finally, it concatenates the hash values and returns the resulting MD5 hash as a 
128-bit (16-byte) value.
"""
def md5(message):
    # Initialize variables
    a0 = 0x67452301
    b0 = 0xEFCDAB89
    c0 = 0x98BADCFE
    d0 = 0x10325476

    # Pre-processing (Padding)
    message = md5_padding(message)

    # Process the message in 512-bit chunks
    for chunk_offset in range(0, len(message), 64):
        chunk = message[chunk_offset:chunk_offset + 64]

        # Initialize hash values for this chunk
        a = a0
        b = b0
        c = c0
        d = d0

        # Main loop
        for i in range(64):
            if i < 16:
                f = (b & c) | ((~b) & d)
                g = i
            elif i < 32:
                f = (d & b) | ((~d) & c)
                g = (5 * i + 1) % 16
            elif i < 48:
                f = b ^ c ^ d
                g = (3 * i + 5) % 16
            else:
                f = c ^ (b | (~d))
                g = (7 * i) % 16

            temp = d
            d = c
            c = b
            b = (b + left_rotate((a + f + int.from_bytes(chunk[4 * g:4 * g + 4], 'little') + 0x5A827999), 7)) & 0xFFFFFFFF
            a = temp

        # Update hash values for this chunk
        a0 = (a0 + a) & 0xFFFFFFFF
        b0 = (b0 + b) & 0xFFFFFFFF
        c0 = (c0 + c) & 0xFFFFFFFF
        d0 = (d0 + d) & 0xFFFFFFFF

    # Concatenate hash values
    return (a0).to_bytes(4, 'little') + (b0).to_bytes(4, 'little') + (c0).to_bytes(4, 'little') + (d0).to_bytes(4, 'little')


import re

"""
Javon: The Simhash class implements a technique for generating a fingerprint of a text 
document called Simhash. It utilizes the MD5 algorithm to hash individual tokens 
of the document and then combines these hashes to produce a unique fingerprint 
representing the document's content. This fingerprint allows for efficient similarity 
comparison between documents based on their tokenized content.
"""
class Simhash:
    #Initializes attributes self.hash and self.hashbits, which can be customized.
    def __init__(self, tokens='', hashbits=64):
        self.hashbits = hashbits
        self.hash = self._simhash(tokens)

    #Returns self.hash as string.
    def __str__(self):
        return str(self.hash)

    #Returns a hash value for a given string using the MD5 algorithm.
    def _string_hash(self, source):
        if source == "":
            return 0
        else:
            return int.from_bytes(md5(source.encode('utf-8')), byteorder='big')  # Modified line

    #Generates a Simhash fingerprint for a list of tokens by computing the weighted sum of their MD5 hash values.
    def _simhash(self, tokens):
        v = [0] * self.hashbits
        for t in [self._string_hash(x) for x in tokens]:
            bitmask = 0
            for i in range(self.hashbits):
                bitmask = 1 << i
                if t & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i
        return fingerprint

    #Calculates the similarity between two Simhash fingerprints by comparing 
    #the Hamming distance between their binary representations
    def similarity(self, other):
        a = self.hash
        b = other.hash
        if a == b:
            return 1
        a = (a ^ (a >> 1)) & ((1 << self.hashbits) - 1)
        b = (b ^ (b >> 1)) & ((1 << self.hashbits) - 1)
        return float(self.hashbits - bin(a ^ b).count('1')) / self.hashbits



# def tokenize(text):
#     # Split the text into tokens (words)
#     words = re.findall(r'\b\w+\b', text.lower())
#     # Return unique tokens
#     return set(words)

# # Example usage:
# stop_words = set(["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"])
        
# document1 = "This is a sample document for simhash implementation asdasd 1213 12312 sss s uci"
# words = re.findall(r'\b[a-z]{3,}\b', document1.lower())
# filtered_words = [word for word in words if word not in stop_words]
# print(filtered_words)
# document2 = "Simhash is used to find similarities between documents"
# document3 = "This is a sample document for simhash implementation"

# # Tokenize the documents
# tokens1 = tokenize(document1)
# tokens2 = tokenize(document2)
# tokens3 = tokenize(document3)

# # Calculate Simhash for each document
# simhash1 = Simhash(tokens1)
# simhash2 = Simhash(tokens2)
# simhash3 = Simhash(tokens3)

# print(type(simhash3.hash))

# # Compute similarity between documents
# print("Similarity between document1 and document2:", simhash1.similarity(simhash2))
# print("Similarity between document1 and document3:", simhash1.similarity(simhash3))
# print("Similarity between document2 and document3:", simhash2.similarity(simhash3))
