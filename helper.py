import csv

class Helper:
    def __init__(self) -> None:
        self.log_name = "log.csv"
        self.freq_log_name = "freq_log.csv"
        self.dumper = []
        self.freq_dict = {}
        self.log = []
        self.known_exact_hash = set()
        self.low_text_tags = {'[document]', 'style', 'footer', 'script', 'meta', 'head', 'link', 'aside', 'nav', 'html', 'input', 'noscript', 'header'}
    
    def load(self):
        with open(self.log_name, "r", encoding='UTF8') as f:
            csvfile = csv.reader(f)
            for line in csvfile:
                line[1] = int(line[1])
                line[2] = int(line[2])
                self.log.append(line)
        
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
        self.log.append(log_entry)
        self.known_exact_hash.add(log_entry[2])
        for word, freq in tokens_dict.items():
            if word in self.freq_dict:
                self.freq_dict[word] += freq
            else:
                self.freq_dict[word] = freq
        if len(self.dumper) == 10:
            self.write()