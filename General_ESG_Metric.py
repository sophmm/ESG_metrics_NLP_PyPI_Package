import nltk
import re  # regular expression
#pip install pymupdf
import fitz
import os
import spacy
from spacy.matcher import PhraseMatcher
#import pandas as pd


class GeneralESGMetric:

    def __init__(self, company_name=[], metric_flag=[], data=[]):
        """ Generic class for the extraction of all ESG metrics from an annual report PDF

        Attributes:
            company_name (string)
            metric_flag (string) representing the disclosure of an ESG metric in the PDF ('T' for True or 'F' for False)
            data (string) - all text data from file as a single string
        """

        self.company = company_name
        self.metric_flag = metric_flag
        self.data = data

    def get_company_name(self, file_name):
        basename_without_ext = os.path.splitext(os.path.basename(file_name))[0]
        company_name = basename_without_ext.replace('_Annual_Report_2020', '')
        self.company = company_name
        return self.company

    def read_pdf_file(self, file_name):
        """
        Function to read in the text from a PDF file as one string.
        To be used internally in children classes.
        Args: PDF: file_name
        Returns : str: all text and tables in pdf
        """
        with fitz.open(file_name) as file:
            all_text = []
            for page_number, page in enumerate(file.pages()):
                a = page.get_text()  # selecting all text
                all_text.append(a)
        all_text = ','.join(all_text)  # as one string
        self.data = all_text
        return self.data

    def _assign_t_f_flag(self, metric):

        if metric != 'F':
            flag = 'T'
        else:
            flag = metric

        self.metric_flag = flag

    def _select_sentences_from_whole_text_using_re(self, key_phrases):
        """
        A function to select sentences from text by tokenizing into sentences, extract the key phrases and
        rejoin the sentences into one string.

        If no sentences are found, the string is set to False.

        Args: list: desired key phases
        Returns: str: sentences with the key phrases in only as a single string
        """
        text = self.data
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

    def _two_stage_sentence_selection(self, key_phrases1, key_phrases2, entity_name):
        """
        A function to initially select sentences containing reference to a broader set of key phrases (key_phrase1)
        using NLTK, and then Spacy's PhraseMatcher identifies sentences with specific words/ phrases (key_phrase2).
        This two-stage filtering narrows down the sentences dramatically to the desired sentence.

        This is a dependency function used within 'extracting_tenure_flag_and_length()' and 'extracting_fee_flag()'

        Args: list: broader (1) and more specific (2) key phrases, and the desired entity name e.g. TENURE or FEES
        Returns: the sentence (/s) with the desired key phrase as one string
        """
        text = self.data

        # 1st filtering of text:
        sel_text = select_sentences_from_whole_text_using_re(key_phrases1)
        # print (sel_text)

        if sel_text:
            # 2nd filtering of text using Spacy PhraseMatcher:
            text = sel_text
            nlp = spacy.load("en_core_web_sm")
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
            return sel_text, _, _, _

    # def _create_truth_df(self, excel_doc):
    #
    #     """"
    #     A function to convert the 'truth' data from an Excel spreadsheet into a dataframe.
    #     The auditor name, tenure and fee columns are selected.
    #     Args: An Excel file
    #     Returns: A dataframe of the 'truth' data
    #     """
    #     df_true = pd.read_excel(excel_doc)
    #     df_true = df_true.sort_values(by=['File name'])
    #     df_true['Company'] = df_true['File name'].apply(lambda x: x.replace('_Annual_Report_2020.pdf', ''))
    #
    #     # selecting columns:
    #     df_true = df_true.filter(items=['Company', 'Is auditor name disclosed?', 'Auditor name',
    #                                     'Is auditor tenure disclosed?', 'Auditor tenure (years)',
    #                                     'Are audit fees disclosed?', 'Are non-audit fees disclosed?',
    #                                     'Anti-Slavery statement present', 'Restatement of Financials',
    #                                     'Reference to SASB or GRI present'])
    #     print('Truth df imported with shape: ', df_true.shape)
    #     return df_true
    #
    # def _merge_predicted_and_true_metrics(self, df_predicted, df_true):
    #
    #     df_full = pd.merge(df_predicted, df_true, on=['Company'])
    #     return df_full
    #


test1 = GeneralESGMetric()
company = test1.get_company_name('Unilever_Annual_Report_2020.pdf')
print(company)

data = test1.read_pdf_file('Unilever_Annual_Report_2020.pdf')
#print(data) #works

