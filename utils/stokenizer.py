class STokenizer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        """
        Generate alphanumeric lower case tokens (0-9, a-z, A-Z),
        dismiss all other characters as seperator.
        :return: tokens
        """
        token = []
        for char in self.text:
            if char.isascii() and char.isalnum():
                token.append(char.lower())
            else:
                if token:
                    yield "".join(token)
                    token = []
        # check the last token
        if token:
            yield "".join(token)

