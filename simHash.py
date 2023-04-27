

def _generate_Hash(word:str) -> str:
    """
    Using a polynomial hash function (base^(lengthOfWord) * letter_mapping),
    generates an 8-bit hash value.
    Credits to Shindler's ICS 46 for hash function
    """
    base = 37
    mod = 4095 # largest value that can be represented by 12-bits

    hash = 0
    word = word.lower()
    for i in range(len(word)):
        asciiRep = ord(word[i]) - ord('a') + 1
        asciiRep %= mod
        temp = base**len(word)
        temp = temp%mod
        hash += (asciiRep * temp)

    return "{0:012b}".format(hash)
    

def generate_Fingerprint(token_Freq:dict):
    hash_dict = dict()

    # generating 12-bit hash values
    for token in token_Freq.keys():
        hash_dict[token] = _generate_Hash(token)

    # vector formed by summing weights
    summingWeights = list()
    for i in range(12):
        sumWeight = 0
        for token in hash_dict.keys():
            _multiplier = 1 if int(hash_dict[token][i]) else -1
            sumWeight += _multiplier*token_Freq[token]
        summingWeights.append(sumWeight)
    
    assert len(summingWeights) == 12, "Incorrect calculation..."

    #12-bit fingerprint formed from summingWeights
    fingerprint = ""
    for val in summingWeights:
        fingerprint += "1" if val > 0 else "0"
    
    return fingerprint


def calc_similarity(f1, f2) -> bool:
    """
    threshold: 0.96
    """
    threshold = 0.96
    
    assert len(f1) == len(f2), "Fingerprints are not same length"

    similar_count = 0
    for i in range(12):
        if f1[i] == f2[i]:
            similar_count += 1
    
    return (similar_count / 12) >= threshold
