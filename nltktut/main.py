import nltk
import json
import re
import string
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('tagsets')
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.stem.porter import PorterStemmer 
from nltk.stem.wordnet import WordNetLemmatizer 
print()
print()
print()

stop_words = stopwords.words('english')

def lemmatize_sentence(sentence):
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(word_tokenize(sentence)):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence


def purify(pstr):
    mainstr = pstr
    splitstr = mainstr.split(" ")
    i=0
    cleanSS = []
    for item in splitstr:
        # Remove URLs
        splitstr[i] = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
           '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', splitstr[i])

        
        if len(item) > 0 and item not in string.punctuation and item.lower() not in stop_words:
            # Get lowercase
            cleanSS.append(splitstr[i])
        i+=1

    cleanStr = ""
    for item in cleanSS:
        cleanStr += item + " "
    cleanStr = cleanStr[:-1]
    # Return purified string

    return str(lemmatize_sentence(cleanStr)).lower()


def tokenizeAndStemPurified(purified):
    final = ""
    purified = purified.replace("'",'"')
    for item in json.loads(purified):
        stem = PorterStemmer()
        item = stem.stem(item)
        final += item + " "
    final = final[:-1]
    final = pos_tag(word_tokenize(final))

    return final

print(tokenizeAndStemPurified(purify("Start Swimming")))