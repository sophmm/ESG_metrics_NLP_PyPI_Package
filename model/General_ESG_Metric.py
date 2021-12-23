import nltk
#nltk.download('punkt')
import re  # regular expression
#pip install pymupdf for fitz
import fitz
import os
import spacy
from spacy.matcher import PhraseMatcher
import en_core_web_sm
from sklearn import metrics
import pandas as pd

def select_sentences_using_re(text, key_phrases):
    """
    A function to select sentences from text by tokenizing into sentences, extract the key phrases and
    rejoin the sentences into one string.

    If no sentences are found, the string is set to False.

    Args: list: desired key phases
    Returns: str: sentences with the key phrases in only as a single string
    """

    sents = nltk.sent_tokenize(text)

    key_phrase_sentences = []
    for key_phrase in key_phrases:
        p = re.compile(key_phrase)
        for sent in sents:
            if p.findall(sent.lower()):
                key_phrase_sentences.append(sent)

    sel_sent_str = ','.join(key_phrase_sentences)  # as one string

    if len(sel_sent_str) == 0:
        sel_sent_str = False

    return sel_sent_str

def create_truth_df(excel_doc):

    """"
    A function to convert the 'truth' data from an Excel spreadsheet into a dataframe.
    The auditor name, tenure and fee columns are selected.
    Args: An Excel file
    Returns: A dataframe of the 'truth' data
    """
    df_true = pd.read_excel(excel_doc)
    df_true = df_true.sort_values(by=['File name'])
    df_true['Company'] = df_true['File name'].apply(lambda x: x.replace('_Annual_Report_2020.pdf', ''))

    # selecting columns:
    df_true = df_true.filter(items=['Company', 'Is auditor name disclosed?', 'Auditor name',
                                    'Is auditor tenure disclosed?', 'Auditor tenure (years)',
                                    'Are audit fees disclosed?', 'Are non-audit fees disclosed?',
                                    'Anti-Slavery statement present', 'Restatement of Financials',
                                    'Reference to SASB or GRI present'])
    #print('Truth df imported with shape: ', df_true.shape)
    return df_true

def merge_predicted_and_true_metrics(df_predicted, df_true):

    df_full = pd.merge(df_predicted, df_true, on=['Company'])
    return df_full

def calculate_accuracy(df_full, predicted_cols, true_cols):
    metrics = []
    accuracies = []
    for i in range(len(predicted_cols)):
        predicted_col_name = predicted_cols[i]
        true_col_name = true_cols[i]
        metrics.append(predicted_col_name)

        correct_pred = df_full.loc[df_full[predicted_col_name] == df_full[true_col_name]]
        incorrect_pred = df_full.loc[df_full[predicted_col_name] != df_full[true_col_name]]

        accuracy = correct_pred.shape[0] / (correct_pred.shape[0] + incorrect_pred.shape[0])
        accuracies.append(accuracy)

    metric_dict = {'Metric': metrics, 'Accuracy': accuracies}
    df_accuracy = pd.DataFrame(metric_dict)

    return df_accuracy

def calculate_evaluation_metrics_for_binary_metrics(df_full, governance_metrics_binary):
    gov_metric = []
    accuracy_score = []
    precision_score = []
    recall_score = []
    f1_score = []
    for governance_metric in governance_metrics_binary:
        y_pred = df_full[governance_metric[0]].replace(('T', 'F'), (1, 0))
        y_true = df_full[governance_metric[1]].replace(('T', 'F'), (1, 0))
        accuracy = metrics.accuracy_score(y_true, y_pred)
        precision = metrics.precision_score(y_true, y_pred)
        recall = metrics.recall_score(y_true, y_pred)
        f1 = metrics.f1_score(y_true, y_pred)
        gov_metric.append(governance_metric[0].replace('Predicted ', ''))
        accuracy_score.append(accuracy)
        precision_score.append(precision)
        recall_score.append(recall)
        f1_score.append(f1)
    evaluation_metrics = {'Governance metric': gov_metric, 'Accuracy': accuracy_score, 'Precision': precision_score,
                          'Recall': recall_score, 'F1 score': f1_score}
    df_evaluation_metrics = pd.DataFrame(evaluation_metrics)
    return df_evaluation_metrics


class GeneralESGMetric:

    def __init__(self, filename, company_name, metric_flag, data):
        """ Generic class for the extraction of all ESG metrics from an annual report PDF

        Attributes:
            filename: pdf file
            company_name (string)
            metric_flag (string) representing the disclosure of an ESG metric in the PDF ('T' for True or 'F' for False)
            data (string) - all text data from file as a single string
        """
        self.filename = filename
        self.company = company_name
        self.metric_flag = metric_flag
        self.data = data

    def get_company_name(self):
        basename_without_ext = os.path.splitext(os.path.basename(self.filename))[0]
        company_name = basename_without_ext.replace('_Annual_Report_2020', '')
        self.company = company_name
        return self.company

    def read_pdf_file(self):
        """
        Function to read in the text from a PDF file as one string.
        To be used internally in children classes.
        Args: PDF: file_name
        Returns : str: all text and tables in pdf
        """
        with fitz.open(self.filename) as file:
            all_text = []
            for page_number, page in enumerate(file.pages()):
                a = page.get_text()  # selecting all text
                all_text.append(a)
        all_text = ','.join(all_text)  # as one string
        self.data = all_text
        return self.data

    def get_disclosure_flag(self, metric):
        #needs editing
        if metric != 'F':
            flag = 'T'
        else:
            flag = metric #'F'

        self.metric_flag = flag
        return

    def two_stage_sentence_selection(self, data, key_phrases1, key_phrases2, entity_name):
        """
        A function to initially select sentences containing reference to a broader set of key phrases (key_phrase1)
        using NLTK, and then Spacy's PhraseMatcher identifies sentences with specific words/ phrases (key_phrase2).
        This two-stage filtering narrows down the sentences dramatically to the desired sentence.

        This is a dependency function used within 'extracting_tenure_flag_and_length()' and 'extracting_fee_flag()'

        Args: list: broader (1) and more specific (2) key phrases, and the desired entity name e.g. TENURE or FEES
        Returns: the sentence (/s) with the desired key phrase as one string
        """
        if data:
            #data is supplied if it's not in class
            pass
        else:
            #otherwise use data in class
            data = self.data

        # 1st filtering of text:
        sel_text = select_sentences_using_re(data, key_phrases1)
        # print (sel_text)

        if sel_text:
            # 2nd filtering of text using Spacy PhraseMatcher:
            text = sel_text
            nlp = en_core_web_sm.load()
            #nlp = spacy.load("en_core_web_sm")
            patterns = [nlp(text) for text in key_phrases2]
            phrase_matcher = PhraseMatcher(nlp.vocab)
            phrase_matcher.add(entity_name, None, *patterns)

            doc = nlp(text)

            # selected sentences:
            sel_text = []
            for sent in doc.sents:
                for match_id, start, end in phrase_matcher(nlp(sent.text)):
                    if nlp.vocab.strings[match_id] in [entity_name]:
                        # displacy.render(sent, style="ent", jupyter=True)
                        each_sent = sent.text
                        sel_text.append(each_sent)
            sel_text = ','.join(sel_text)  # as one string

            return doc, phrase_matcher, nlp, sel_text
        else:
            #sel_text is empty
            return sel_text,[],[],[]






