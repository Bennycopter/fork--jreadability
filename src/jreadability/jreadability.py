"""
jreadability.jreadability

This module defines the `compute_readability` function.
There are no other public functions, classes or variables.
"""

from fugashi import Tagger
from typing import List, Optional
from fugashi.fugashi import UnidicNode

def compute_readability(text: str, tagger: Optional[Tagger]=None) -> float:
    """
    Computes the readability of a Japanese text.

    Args:
        text (str): The text to be scored.
        tagger (Optional[Tagger]): The fugashi parser used to parse the text. 

    Returns:
        float: A float representing the readability score of the text.
    """

    if tagger is None:
        # initialize mecab parser
        tagger = Tagger()

    doc = tagger(text)

    def split_japanese_sentences(doc: List[UnidicNode]) -> List[List[UnidicNode]]:
        """
        Helper function that breaks the parsed text into lists of sentences.
        """
        
        sentences = []
        current_sentence = []
        for token in doc:
            current_sentence.append(token)
            
            if token.surface in ('。', '？', '！', '．'):
                sentences.append(current_sentence)
                current_sentence = []
        
        # if there's any leftover sentence that doesn't end with sentence-ending punctuation
        if current_sentence:
            sentences.append(current_sentence)

        return sentences

    # first, compute mean sentence length (in words, not characters)
    sentences = split_japanese_sentences(doc)
    
    sentence_lengths = []
    for sentence_doc in sentences:
    
        words_per_sentence = len(sentence_doc)
        sentence_lengths.append(words_per_sentence)
    
    mean_length_of_sentence = sum(sentence_lengths) / len(sentences)

    # next, compute proportion of kango, wago, verbs and auxiliary verbs
    num_kango = 0
    num_wago = 0
    num_verbs = 0
    num_aux_verbs = 0
    for token in doc:

        goshu = token.feature.goshu # goshu (語種) is the word's origin
        pos = token.feature.pos1

        if goshu == '漢': # 'kan', meaning chinese
            num_kango += 1
        elif goshu == '和': # 'wa', meaning japanese
            num_wago += 1

        if pos == '動詞': # 'doushi', meaning verb
            num_verbs += 1
        elif pos == '助動詞': # 'jodoushi', meaning auxiliary verb
            num_aux_verbs += 1
    
    proportion_of_kango = 100.0 * num_kango / len(doc)
    proportion_of_wago = 100.0 * num_wago / len(doc)
    proportion_of_verbs = 100.0 * num_verbs / len(doc)
    proportion_of_aux_verbs = 100.0 * num_aux_verbs / len(doc)

    readability_score = mean_length_of_sentence * -0.056 + \
                        proportion_of_kango * -0.126 + \
                        proportion_of_wago * -0.042 + \
                        proportion_of_verbs * -0.145 + \
                        proportion_of_aux_verbs * -0.044 + \
                        11.724
    
    return readability_score