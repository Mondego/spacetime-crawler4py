import csv

class Helper:
    def __init__(self) -> None:
        self.log_name = "log.csv"
        self.freq_log_name = "freq_log.csv"
        self.dumper = []
        self.freq_dict = {}
        self.known_exact_hash = set()
        #self.low_text_tags = {'[document]', 'style', 'footer', 'script', 'meta', 'head', 'link', 'aside', 'nav', 'html', 'input', 'noscript', 'header'}
        self.stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with',
                              'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's',
                              'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through',
                              'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to',
                              'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does',
                              'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself',
                              'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my',
                              'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}
    
    def load(self):
        with open(self.log_name, "r", encoding='UTF8') as f:
            csvfile = csv.reader(f)
            for line in csvfile:
                self.known_exact_hash.add(int(line[2]))
        
        with open(self.freq_log_name, "r", encoding='UTF8') as f:
            csvfile = csv.reader(f)
            for line in csvfile:
                self.freq_dict[line[0]] = int(line[1])
        
    def write(self):
        with open(self.log_name, "a", encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerows(self.dumper)
            self.dumper.clear()
        with open(self.freq_log_name, "w", encoding='UTF8') as f:
            writer = csv.writer(f)
            for k, v in self.freq_dict.items():
                writer.writerow([k, v])

    def add(self, log_entry, tokens_dict):
        self.dumper.append(log_entry)
        self.known_exact_hash.add(log_entry[2])
        for word, freq in tokens_dict.items():
            if word in self.freq_dict:
                self.freq_dict[word] += freq
            else:
                self.freq_dict[word] = freq
        if len(self.dumper) == 50:
            self.write()