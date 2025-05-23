import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP NP VP NP | NP VP VP | NP VP VP NP
AP -> Adj | Adj NP
NP -> N | Det NP | AP | N PP | Conj N | N NP | N AP | N Conj NP | N Adv
PP -> P | P NP
VP -> V | V NP | V NP PP | V Adv | Conj V | Det V | V PP | Adv V
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # tokenize all words in the sentence
    token_list = nltk.tokenize.word_tokenize(sentence)
    # filter out words with atleast one alpha and lower case
    filtered = [s.lower() for s in token_list if any(c.isalpha() for c in s)]
    return filtered


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # initialize result of nps
    nps = []
    # check all child trees which are NP
    for child in tree.subtrees(lambda t: t.label() == "NP"):
        is_np = True
        # check if any sub child is also NP
        for sub in child.subtrees():
            if sub != child and sub.label() == "NP":
                is_np = False
        # if no child which is NP add to result
        if is_np:
            nps.append(child)
    return nps


if __name__ == "__main__":
    main()
