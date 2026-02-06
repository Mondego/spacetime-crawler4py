import sys
from typing import Dict, Iterable

def tokenize(file_path: str) -> Iterable[str]:
    """
    Runtime Complexity: O(n), where n is the number of characters in the file.
    Each character is examined exactly once, so time complexity depends on how many
    characters we end up reading.
    
    Reads a text file and yields tokens one by one.
    A token is sequence of alphanumeric characters, independent of capitalization.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            token_chars = []   
            
            while True:
                # Read file into chunks to avoid reading entire file into computer RAM. Good for large files
                chunk = f.read(4096)
                if not chunk:
                    break
                
                for ch in chunk:
                    # no .isalphanum() to ensure no incorrect characters sneak in
                    if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or ('0' <= ch <= '9'):
                        token_chars.append(ch.lower())
                    else:
                        if token_chars:
                            yield ''.join(token_chars)
                            token_chars.clear()
                            
            if token_chars:
                yield ''.join(token_chars)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied to read '{file_path}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    
def compute_word_frequencies(tokens: Iterable[str]) -> Dict[str, int]:
    """
    Runtime Complexity: O(m), where m is the number of tokens.
    Each token is processed exactly once, so time complexity depends on how many
    tokens we have.
    
    Computes the frequency of each unique token from the iterable of tokens.
    Returns a dictionary mapping tokens to their frequencies.
    """
    frequencies: Dict[str, int] = {}
    
    for token in tokens:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1
            
    return frequencies


def print_frequencies(frequencies: Dict[str, int]) -> None:
    """
    Runtime Complexity: O(k log k), where k is the number of unique tokens.
    Sorting the tokens by frequency takes O(k log k) time and "dominates" the overall complexity.

    Prints tokens and their frequencies
    Tokens are printed in descending order of frequency.
    """
    sorted_tokens = sorted(frequencies.items(), key=lambda x: (-x[1], x[0]))
    
    for token, freq in sorted_tokens:
            print(f"{token}\t{freq}")
            
            
def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python PartA.py <file_path>", file=sys.stderr)
        sys.exit(1)
    
    tokens = tokenize(sys.argv[1])
    frequencies = compute_word_frequencies(tokens)
    print_frequencies(frequencies)
    
if __name__ == "__main__":
    main()