import hashlib


NUM_BITS = 128 # md5 returns 128 bits


def hash(word: str) -> int:
    return int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)


def get_simhash(word_frequencies: dict) -> int:
    sum_of_weights = [0] * NUM_BITS
    
    for word, frequency in word_frequencies.items():
        hash_of_word = hash(word)

        for i in range(NUM_BITS):
            mask = 1 << i                     # bit mask
            mask_result = hash_of_word & mask # if bit is 0, this will be 0 (so it will evaluate to false in boolean expression)
            sum_of_weights[-i - 1] += frequency if mask_result else -frequency
    
    simhash_str = ''

    for num in sum_of_weights:
        simhash_str += '1' if num >= 0 else '0'
    
    return int(simhash_str, 2) # the second argument "2" means it will evaluate this in binary and return a base-10 integer

def get_similarity(simhash1: int, simhash2: int) -> float:
    num_matching_bits = 0

    for i in range(NUM_BITS):
        mask = 1 << i

        if (simhash1 & mask) == (simhash2 & mask):
            num_matching_bits += 1
    
    return num_matching_bits / NUM_BITS
