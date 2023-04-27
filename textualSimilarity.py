import hashlib

class simHash():
    # tokenDict = {"token": [0, "hashValue"]}
    # The token dict is of the form where the key is the token from the tokenLst, and the 
    # value is a list of 2 elements. On index 0, we have the frequency/weight of the token, and 
    # on index 1 we have the hashEncoding corresponding to the token. 
    tokenDict = dict()
    
    
    def hashConverter(self, integerHash: str) -> str:
        # This method converts the integerHash (ex: 24896731) into a binaryHash(ex: 11010100) using self-made
        # conversion method. It takes the integerHash as an attribute and returns the binaryHash as a string.
        binaryHashNumber = ""
        # The integerHash is a string of an 8 digit number encoded using SHA256 and hexdigest.
        for number in integerHash:
            # Check if the digit <= 4. If so, correspond it to binary number 0.
            if int(number) <= 4: binaryHash += "0"
            # Otherwise, correspond it to binary number 1.
            else: binaryHash += "1"
        return binaryHashNumber
    
    
    @classmethod
    def tokenDictionaryMapper(cls, tokenLst: list) -> None:
    # This method takes the tokenLst as an attribute, and updates the tokenDict with the frequency/weight of 
    # the tokens in the tokenLst. It also updates the binaryHash value of the tokens.
        for token in tokenLst:
            try:
                # update the weight if token already in tokenDict.
                cls.tokenDict[token][0] += 1
            except KeyError:
                # otherwise, create a new entry of the token in the tokenDict.
                cls.tokenDict[token] = [1, ""]
    
        for key in cls.tokenDict.keys():
            # First, we hash ever token using sha256 and hexdigest from the hashlib library. We then convert
            # the hexadecimal into an integer and then only consider the first 8 digits for simiplicity.
            # Reference to converting string to 8 bit binary number: https://stackoverflow.com/a/42089311
            integerHash = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % 10**8
            
            # Then, convert the integer into a binary number using self-created conversion. Finally, update
            # the hashvalue as a binary in the tokenDict.
            binaryHashEncoding = cls.hashConverter(str(integerHash))
            cls.tokenDict[key][1] = binaryHashEncoding
    
    
    def simHashFingerprint(self) -> str:
        # This method returns the fingerprint of the entire webpage.
        vector = []
        for index in range(8):
            number = 0
            # Iterate over all the tokens in tokenDict.
            for key in self.tokenDict.keys():
                # Use simhashing technique to find an integer value to append to the length 8 list.
                if self.tokenDict[key][1][index] == "1": number += self.tokenDict[key][0]
                else: number -= self.tokenDict[key][0]
            self.vector.append(number)
        # Declare the fingerprint string
        fingerPrint = ""
        for num in vector:
            # Iterate over the vector with 8 integers. Re-convert into binary
            # depending on the modularity of the number. 
            if num < 0: fingerPrint += "0"
            else: fingerPrint += "1"
        return fingerPrint
    
    
    def similarityChecker(self, simhash1: str, simhash2: str) -> bool:
        similarityIndex = 0
        thresholdLevel = 0.9
        for index in range(len(simhash1)):
            # Find the similarityIndex given simhashes of 2 different webpages.
            if simhash1[index] == simhash2[index]: similarityIndex += 1
        # return a boolean value relative to the threshold value.
        if similarityIndex/8 >= thresholdLevel: return True
        else: return False
            
    