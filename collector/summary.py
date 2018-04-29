#encoding = utf8

from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import numpy as np
from collector.singleton import Singleton
from collector.model import Article


stop = [
"a", "about", "above", "across", "after", "afterwards", "again", "against",
"all", "almost", "alone", "along", "already", "also", "although", "always",
"am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
"any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
"around", "as", "at", "back", "be", "became", "because", "become",
"becomes", "becoming", "been", "before", "beforehand", "behind", "being",
"below", "beside", "besides", "between", "beyond", "bill", "both",
"bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
"could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
"down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
"elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
"everything", "everywhere", "except", "few", "fifteen", "fifty", "fill",
"find", "fire", "first", "five", "for", "former", "formerly", "forty",
"found", "four", "from", "front", "full", "further", "get", "give", "go",
"had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
"hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
"how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
"interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
"latterly", "least", "less", "ltd", "made", "many", "may", "me",
"meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
"move", "much", "must", "my", "myself", "name", "namely", "neither",
"never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
"nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
"once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
"ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
"please", "put", "rather", "re", "same", "see", "seem", "seemed",
"seeming", "seems", "serious", "several", "she", "should", "show", "side",
"since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
"something", "sometime", "sometimes", "somewhere", "still", "such",
"system", "take", "ten", "than", "that", "the", "their", "them",
"themselves", "then", "thence", "there", "thereafter", "thereby",
"therefore", "therein", "thereupon", "these", "they", "thick", "thin",
"third", "this", "those", "though", "three", "through", "throughout",
"thru", "thus", "to", "together", "too", "top", "toward", "towards",
"twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
"very", "via", "was", "we", "well", "were", "what", "whatever", "when",
"whence", "whenever", "where", "whereafter", "whereas", "whereby",
"wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
"who", "whoever", "whole", "whom", "whose", "why", "will", "with",
"within", "without", "would", "yet", "you", "your", "yours", "yourself",
"yourselves"]  

def remove_stop_words(document):
    """Returns document without stop words"""
    document = ' '.join([i for i in document.split() if i not in stop])
    return document

def similarity_score(t, s):
    """Returns a similarity score for a given sentence.
    similarity score = the total number of tokens in a sentence that exits
                        within the title / total words in title
    """
    t = remove_stop_words(t.lower())
    s = remove_stop_words(s.lower())
    t_tokens, s_tokens = t.split(), s.split()
    similar = [w for w in s_tokens if w in t_tokens]
    score = (len(similar) * 0.1 ) / len(t_tokens)
    return score

# generate summary from idf
def genSummary(v, title, doc): 
	NOUNS = ['NN', 'NNS', 'NNP', 'NNPS']
	sents = nltk.sent_tokenize(doc)
	sentences = [nltk.word_tokenize(sent) for sent in sents]
	sentences = [[w for w in sent if nltk.pos_tag([w])[0][1] in NOUNS]
	                  for sent in sentences]

	tfidf = v.transform([doc]).toarray()[0]
	feature_names = v.get_feature_names()
	
	tfidf_sent = [[tfidf[feature_names.index(w.lower())]
                   for w in sent if w.lower() in feature_names]
                 for sent in sentences]
	doc_val = sum(tfidf)
	sent_values = [sum(sent) / doc_val for sent in tfidf_sent]

	similarity_scores = [similarity_score(title, sent) for sent in sents]

	scored_sents = np.array(sent_values) + np.array(similarity_scores)

	indices = np.argsort(scored_sents)
	top = [sents[i] for i in indices][-5:]
	return top[::-1][0]

class Summary(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.idf = self.load_and_train()
        if not self.idf:       
            pass

    def gen(self, title, doc): 
        if not self.idf:
            return ""
        NOUNS = ['NN', 'NNS', 'NNP', 'NNPS']
        sents = nltk.sent_tokenize(doc)
        sentences = [nltk.word_tokenize(sent) for sent in sents]
        sentences = [[w for w in sent if nltk.pos_tag([w])[0][1] in NOUNS]
                          for sent in sentences]
        
        tfidf = self.idf.transform([doc]).toarray()[0]
        feature_names = self.idf.get_feature_names()
        
        tfidf_sent = [[tfidf[feature_names.index(w.lower())]
                       for w in sent if w.lower() in feature_names]
                     for sent in sentences]
        doc_val = sum(tfidf)
        sent_values = [sum(sent) / doc_val for sent in tfidf_sent]
        
        similarity_scores = [similarity_score(title, sent) for sent in sents]
        
        scored_sents = np.array(sent_values) + np.array(similarity_scores)
        
        indices = np.argsort(scored_sents)
        top = [sents[i] for i in indices][-5:]
        return top[::-1][0]
    
    def load_and_train(self):
        train = [row.content for row in Article.select(Article.content)]
        if len(train) == 0:
            return

        v = TfidfVectorizer(stop_words=stop,norm='l2')
        v.fit(train)
        return v

