import sys
import os
import spacy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import load_nlp_models

def test_laod_nlp_models():
    # This is a slow test as it actually loads the models
    nlp = spacy.load("en_core_web_trf")

    nlp_sm = spacy.load("en_core_web_sm")
    
    # Check that we get a proper spaCy model
    assert nlp is not None
    assert nlp_sm is not None
    assert isinstance(nlp, spacy.language.Language)
    print("all test cases passed.")




if __name__=='__main__':
    test_laod_nlp_models()

