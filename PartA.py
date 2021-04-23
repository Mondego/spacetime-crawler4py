import string, sys, re

class Token:
	def __init__(self, word):
		self._word = word

# for large n, this implementation will run in O(n) times for n = number of words in the document
# seperated by spaces because each invidual word will be processed at most once. All functions inside
# processing of the word is less than O(n)
def tokenize(TextFilePath):
	toReturn = []
	with open(TextFilePath, 'r') as file:
		for line in file:
			for word in line.split():
				word = word.strip().lower()

				# if non english characters, continue to the next word
				try: word.encode(encoding='utf-8').decode('ascii')
				except UnicodeDecodeError:
					continue
				
				else:
					# remove leading and trailing punctuation
					while len(word) >= 0:
						if word[0] in string.punctuation:
							word = word.replace(word[0], "", 1)
						else:
							if word[-1] in string.punctuation:
								word = word.replace(word[-1], "", 1)
						if len(word) == 0:
							break
						if word[0] not in string.punctuation and word[-1] not in string.punctuation:
							break

					# if more than 1 consecutive punctuation, replace all punctuation with space and 
					# store each word seperately in the dictionary
					# the below block of code will run through the word only once
					consec_punc = False
					if len(word) >= 2:
						for i in range(0, len(word)-2):
							if word[i] in string.punctuation and word[i+1] in string.punctuation:
								consec_punc = True
								word = word.replace(word[i], ' ', 1)
								word = word.replace(word[i+1], ' ', 1)
								for j in range(i+2, len(word)-1):
									if word[j] in string.punctuation:
										word = word.replace(word[j], ' ')
								word = word.replace(' ', '')
								if len(word) != 0:
									toReturn.append(word)
								break

					# if is above case, go to the next word
					if consec_punc == True:
						continue
					else:
						# store the word as is, with the punctuation in place
						toReturn.append(word)

						# if there are only numbers and punctuation, go to next word
						if not word.isalpha():
							continue
						else:
							# if there are punctuations in the word, also store the words seperately as tokens
							for c in word:
								if c in string.punctuation:
									word = word.replace(c, ' ')

							toSave = word.strip().split()
							for item in toSave:
								toReturn.append(item)
	return toReturn

# for large n, this algorithm will run in O(n) times for n = number of words in the document 
# which were turn into individual tokens by tokenize function. (worse case)
# each token will go through the if else statement once (processed once)
def computeWordFrequencies(TokenList):
	toReturn = {}
	for i in TokenList:
		if i not in toReturn:
			toReturn[i] = 1
		else:
			toReturn[i] = toReturn[i] + 1
	return toReturn

# for large n, this algorithm will run in O(n log n) times where n = number of words in the document
# print and items function both runs in O(n) times but sorted runs in O(n log n) time documented
# by python website. the sorted function implements the Timsort, where if input is less than 64, it 
# implements the binary insertion sort and when greater than 64 implements a more advance version
# of merge sort. The combination of the two allows this sorted algorithm to be more efficient 
# achieving the average case of O(n log n). Since other functions, namely print and items runs at
# O(n) which grow slower than n log n, this algorithm will be in O(n log n) time complexity. 
def printFrequencies(FrequencyMap):
	sorted_fm = sorted(FrequencyMap.items(), key=lambda x:x[1], reverse=True)
	for i in sorted_fm:
		print(i[0],i[1])

# runs in maximum time complexity of the three functions
def main():
	tokens_list = tokenize(sys.argv[1])
	token_frequencies = computeWordFrequencies(tokens_list)
	printFrequencies(token_frequencies)

if __name__ == '__main__':
	main()