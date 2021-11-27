import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy.lang.en import English
from spacy.training import Example
from spacy import displacy
from collections import Counter
import random
import nltk
import re #regular expression
import fitz
import glob
import os
import pandas as pd
import sklearn
from statistics import mode
from functools import reduce
from datetime import date
import numpy as np

from General_ESG_Metric import GeneralESGMetric, select_sentences_using_re
from Training_data_strings import patterns, NAME_TEXT

def create_Spacy_training_data_for_auditor_name(patterns, NAME_TEXT):
    """
    The training data for the customer NER model is created by identifying and locating the
    patterns (auditor company names) in the sentences in NAME_TEXT.

    The training data uses text from 23/77 (~30%) company reports:
    Reckitt, Weir Group, Prudential, Brit. Land, Informa, Rolls-Royce, Smurfit/kappa, XP Power, Morrisons, Pirelli, SSE,
    Severn Treut, BHP, Entain, Ferguson, Royal Mail, Smiths Groups, Barclays, Autotrader, BAE, Microsoft, Kingfisher, Anglo-American

    Input: sentences to train the model on (NAME_TEXT) and the auditor names (patterns)
    Output: a list of each training sentence with the position of the auditor's name and the label

    Known problems to fix:
       - no negative examples (i.e. sentences without the auditor name) are currently given.
    """

    nlp = English()
    matcher = Matcher(nlp.vocab)
    # Add patterns to the matcher
    matcher.add("AUDITOR", patterns)

    TRAINING_DATA = []
    ALL_ENTITIES = []
    for doc in nlp.pipe(NAME_TEXT):
        # Match on the doc and create a list of matched spans
        spans = [doc[start:end] for match_id, start, end in matcher(doc)]

        # Get (start character, end character, label) tuples of matches
        entities = [(span.start_char, span.end_char, "AUDITOR") for span in spans]
        # print (entities)

        # Format the matches as a (doc.text, entities) tuple
        training_example = (doc.text, {"entities": entities})

        # Append the example to the training data
        TRAINING_DATA.append(training_example)
        ALL_ENTITIES.append(entities)

    # print('Training data:', *TRAINING_DATA, sep="\n")
    # print ('All entities in training data:', ALL_ENTITIES)

    return TRAINING_DATA


def train_spacy_model(data, iterations, blank_model=True):
    """
    A function to train the custom NER model and disable other pipes for optimization

    Input: training data, the number of iterations and whether the customer entities
    are added either to a blank or standard NER model

    Output: customised NER model
    """

    TRAIN_DATA = data

    if blank_model:
        nlp = spacy.blank('en')  # create blank Language class
        # create the built-in pipeline components and add them to the pipeline
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe('ner')
            nlp.add_pipe('sentencizer')
    else:
        nlp = spacy.load('en_core_web_sm')
        ner = nlp.create_pipe('ner')

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']

    with nlp.disable_pipes(*other_pipes):  # only train NER

        if blank_model:
            optimizer = nlp.begin_training()

        for itn in range(iterations):
            # print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                # Update the model
                nlp.update([example], losses=losses)
            # print(losses)
    return nlp

def find_auditor_name_using_frequency(tagged_entities_list):
    """
    A function to name abbrev. to full auditor name, and selecting most frequent name as current auditor
    (often the case & quickest option).
    If the auditor name tag is outside big 4 --> search for one of the big 4 in the 'tagged_entities_list' to double check

    Input: List of tagged entities using the 'Auditor' tag
    Output: Single auditor name
    """
    modified_tagged_entities_list = [x.replace('PwC', 'PricewaterhouseCoopers') for x in tagged_entities_list]
    modified_tagged_entities_list = [x.replace('EY', 'Ernst & Young') for x in modified_tagged_entities_list]
    auditor_name = mode(modified_tagged_entities_list)

    if (auditor_name != 'KPMG') & (auditor_name != 'PricewaterhouseCoopers') & \
            (auditor_name != 'Ernst & Young') & (auditor_name != 'Deloitte') & (auditor_name != 'PwC'):

        big4names = 'KPMG|PricewaterhouseCoopers|Ernst & Young|Deloitte'
        tagged_entities_str = ','.join(modified_tagged_entities_list)  # as one string

        # find all big4 names in the tagged entities
        all_names = re.findall(big4names, tagged_entities_str)
        if len(all_names) == 0:
            auditor_name = 'F'
        else:
            # selecting most frequency name as current auditor
            auditor_name = mode(all_names)

    return auditor_name


class AuditorName(GeneralESGMetric):
    """ A class to extract the current auditor name from ESG reports

      Attributes:
            filename: pdf file
            company_name (string)
            metric_flag (string): representing the disclosure of an ESG metric in the PDF
            ('T' for True or 'F' for False)
            data (string): all text data from file as a single string
            auditor_name (string)
    """

    def __init__(self, filename, company_name, metric_flag, data, auditor_name):

        GeneralESGMetric.__init__(self, filename, company_name, metric_flag, data)
        self.auditor_name = auditor_name


    def get_auditor_name(self, sel_text, custom_nlp_model):
        """
        A function to extract the auditor name and T/F binary classification from ESG reports.
        It initially selects sentences containing reference to the auditor name
        using NLTK and runs them through a custom NER tagger.
        The most frequent auditor name is selected, and if this is not one of the big 4,
        double check if it's found in the tagged entities at all.

        Input: All text in pdf file as a single string
        Output: auditor name and auditor flag (True/False)
        """

        if sel_text:
            # run NER model:
            doc = custom_nlp_model(sel_text)
            tagged_entities_list = [(ent.text) for ent in doc.ents]
            # displacy.render(doc, style="ent", jupyter=True)

            if len(tagged_entities_list) == 0:
                # no tagged entities in selected sentences
                auditor_name = 'F'
            else:
                auditor_name = find_auditor_name_using_frequency(tagged_entities_list)
        else:
            # no selected sentences to find auditor
            auditor_name = 'F'

        self.auditor_name = auditor_name
        return self.auditor_name

#testing:

# # Create custom NER model
# TRAINING_DATA = create_Spacy_training_data_for_auditor_name(patterns, NAME_TEXT)
# custom_nlp_model = train_spacy_model(TRAINING_DATA, 30, blank_model=True) #performs better on blank model
#
# #testing one company
# name_test = AuditorName('data_test_set/Unilever_Annual_Report_2020.pdf', [],[],[],[])
# data = name_test.read_pdf_file()
#
# key_phrases = ['external auditor', 'statutory auditor', 'independent auditor', 'auditor', 'audit',
#                'for an on behalf of']
#
# sel_text = select_sentences_using_re(data, key_phrases)
#
# auditor_name = name_test.get_auditor_name(sel_text, custom_nlp_model)
# name_test.get_disclosure_flag(auditor_name)
#
# print (name_test.auditor_name)
# print (name_test.metric_flag)



