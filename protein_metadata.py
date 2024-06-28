#
# Protein Word
#
class ProteinWord:
    def __init__(self, type, text, start, end):
        self.type = type
        self.text = text
        self.start = start
        self.end = end

    def __str__(self):
        return f' {self.type}, {self.text}, {self.start}, {self.end}'

    def __repr__(self):
        return f' {self.type}, {self.text}, {self.start}, {self.end}'
    
#
# Protein Sentence
#
class ProteinSentence:
    def __init__(self, uniprot_id, word):
        #print('Creating new sentence for', uniprot_id, ': ',  word.text)
        self.uniprot_id = uniprot_id
        self.words = [word]
        self.text = word.text
        
    def add_word(self, word):
        #print('Adding new word to', self.uniprot_id, ':',  word.text)
        self.words.append(word)
        self.text = self.text + ',' + word.text
        
    def __str__(self):
        return f' {self.uniprot_id}: {self.text}'

    def __repr__(self):
        return f' {self.uniprot_id}: {self.text}'
        