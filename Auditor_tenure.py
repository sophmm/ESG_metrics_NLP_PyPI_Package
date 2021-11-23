import re
from datetime import date
import numpy as np
from .General_ESG_Metric import GeneralESGMetric


class Tenure(GeneralESGMetric):
    """ A class ...

      Attributes:
            company_name (string)
            metric_flag (string): representing the disclosure of an ESG metric in the PDF
            ('T' for True or 'F' for False)
            data (string): all text data from file as a single string
            years (int): the tenure of the current auditor (in years)
    """

    def __init__(self, company_name=[], metric_flag=[], data=[], years=[]):

        GeneralESGMetric.__init__(self, company_name, metric_flag, data)
        self.tenure_yrs = years

    def _find_tenure_from_min_year(self, all_no, todays_date):
        """
        A function to extract the length of the auditor tenure period in years.
        First all years are selected (assuming numbers with 4 digits are years).
        Then the minimum year is used as the start of the tenure, otherwise 'F' is returned as False.

        This is a dependency function used within 'extracting_tenure_flag_and_length()'

        Args: a list of numbers and the today's date
        Returns: the tenure length
        """

        all_years = [x for x in all_no if len(x) == 4]
        if all_years:  # years found within the numbers
            all_years = [int(i) for i in all_years]
            yrs_since = np.min(all_years)
            # print ('yrs_since: ', yrs_since)
            tenure_length = (todays_date.year - yrs_since)
        else:  # no years given
            tenure_length = 'F'

        return tenure_length

    def extracting_tenure_flag_and_length(self):
        """
        A function to extract the auditor tenure (in years) and T/F binary classification from ESG reports,
        using two-stage sentence selection.

        Years (2021 & 2020) are removed, a date with a month and year supplied is searched for,
        otherwise the minimum year in the text is used to find the start of the appointed tenure period.
        Using NER tagger with 'DATE' didn't work well to select dates
    #         doc = nlp(sel_text)
    #         dates = [ent.lemma_ for ent in doc if ent.ent_type_ == "DATE"]

        Returns: Tenure length (in years) and flag (True/False)
        """
        all_text = self.data
        key_phrases1 = ['external auditor', 'statutory auditor', 'independent auditor',
                        'audit tender', 'appointed as external auditor', 'reappointment'
                                                                         'has been the Group’s auditor since',
                        'was the auditor',
                        'formal tender process', 'first appointed', 'competitive retender in',
                        'competitive tender process']

        key_phrases2 = ('appointed', 'reappointed', 'first appointed', 'since')  # 'tender process'

        entity_name = 'TENURE'
        todays_date = date.today()

        doc, phrase_matcher, nlp, sel_text = two_stage_sentence_selection(all_text, key_phrases1, key_phrases2,
                                                                          entity_name)
        # print (doc)
        if doc:
            sel_text = str(sel_text)  # ensuring text is a string
            if '2021' in sel_text.split(): sel_text = sel_text.replace('2021', '')
            # if '2020' in sel_text.split(): sel_text = sel_text.replace('2020', '')

            # print (sel_text)

            # finding month in sel_text:
            pattern = '|'.join(month_name[1:])
            month = re.search(pattern, sel_text, re.IGNORECASE)
            if month:
                month = month.group(0)
                # print (month)
                # splitting string after month
                split_word = month
                rest = sel_text.partition(split_word)[2]

                # extract numbers in string & assume 1st number after the month is the first appointed year:
                all_no = re.findall("\d+", rest)
                if all_no:
                    if len(all_no[0]) == 4:
                        # next number is 4 digits i.e. a year
                        yrs_since = int(all_no[0])
                        # print ('yrs_since: ', yrs_since)
                        tenure_length = (todays_date.year - yrs_since)
                    else:
                        # no year supplied after month so use the minimum year given in the text:
                        tenure_length = find_tenure_from_min_year(all_no, todays_date)
                else:
                    # print ('No numbers after month given')
                    all_no = re.findall("\d+", sel_text)
                    tenure_length = find_tenure_from_min_year(all_no, todays_date)
            else:
                # no month is supplied in text so use the minimum year given in the text:
                # print ('No month given')
                all_no = re.findall("\d+", sel_text)
                tenure_length = find_tenure_from_min_year(all_no, todays_date)
        else:
            tenure_length = 'F'

        # print ('Tenure_length: ', tenure_length)

        tenure_flag = assigning_T_F_flag_for_classification(tenure_length)

        self.tenure_yrs = tenure_length
        self.metric_flag = tenure_flag

        return self.metric_flag, self.tenure_yrs

# testing
# tenure_test = Tenure()
# tenure_test.read_pdf_file('Unilever_Annual_Report_2020.pdf')
# flag, tenure = tenure_test.extracting_tenure_flag_and_length()


