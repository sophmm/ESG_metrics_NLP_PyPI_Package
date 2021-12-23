import re
from datetime import date
import numpy as np
from calendar import month_name
from General_ESG_Metric import GeneralESGMetric


def find_tenure_from_min_year(all_no, todays_date):
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


class Tenure(GeneralESGMetric):
    """ A class to extract the auditor tenure (in years) from ESG reports.

      Attributes:
            filename: pdf file
            company_name (string)
            metric_flag (string): representing the disclosure of an ESG metric in the PDF
            ('T' for True or 'F' for False)
            data (string): all text data from file as a single string
            years (int): the tenure of the current auditor (in years)
    """

    def __init__(self, filename, company_name, metric_flag, data, years):

        GeneralESGMetric.__init__(self, filename, company_name, metric_flag, data)
        self.tenure_yrs = years

    def get_tenure_length(self, sel_text):
        """
        A function to extract the auditor tenure (in years) from ESG reports.

        A date with a month and year supplied is searched for (note current year (2021) is removed from the search)
        otherwise the minimum year in the text is used to find the start of the appointed tenure period.

        Args: sel_text : string of text to extract the tenure from.
        Returns: Tenure length (in years)
        """
        todays_date = date.today()

        if sel_text:
            sel_text = str(sel_text)  # ensuring text is a string
            if '2021' in sel_text.split(): sel_text = sel_text.replace('2021', '')
            # if '2020' in sel_text.split(): sel_text = sel_text.replace('2020', '')

            # finding month in sel_text:
            pattern = '|'.join(month_name[1:])
            month = re.search(pattern, sel_text, re.IGNORECASE)
            if month:
                month = month.group(0)
                # splitting string after month
                split_word = month
                rest = sel_text.partition(split_word)[2]

                # extract numbers in string & assume 1st number after the month is the first appointed year:
                all_no = re.findall("\d+", rest)
                if all_no:
                    if len(all_no[0]) == 4:
                        # next number is 4 digits i.e. a year
                        yrs_since = int(all_no[0])
                        #print ('yrs_since: ', yrs_since)
                        tenure_length = (todays_date.year - yrs_since)
                    else:
                        # no year supplied after month so use the minimum year given in the text:
                        tenure_length = find_tenure_from_min_year(all_no, todays_date)
                else:
                    #print ('No numbers after month given')
                    all_no = re.findall("\d+", sel_text)
                    tenure_length = find_tenure_from_min_year(all_no, todays_date)
            else:
                # no month is supplied in text so use the minimum year given in the text:
                #print ('No month given')
                all_no = re.findall("\d+", sel_text)
                tenure_length = find_tenure_from_min_year(all_no, todays_date)
        else:
            tenure_length = 'F'

        self.tenure_yrs = tenure_length
        return self.tenure_yrs

# testing
# tenure_test = Tenure('data_test_set/Unilever_Annual_Report_2020.pdf', [],[],[],[])
# tenure_test.read_pdf_file()
#
# key_phrases1 = ['external auditor', 'statutory auditor', 'independent auditor',
#                 'audit tender', 'appointed as external auditor', 'reappointment'
#                 'has been the Group’s auditor since',
#                 'was the auditor',
#                 'formal tender process', 'first appointed', 'competitive retender in',
#                 'competitive tender process']
# key_phrases2 = ('appointed', 'reappointed', 'first appointed', 'since')  # 'tender process'
# entity_name = 'TENURE'
#
# _,_,_, sel_text = tenure_test.two_stage_sentence_selection([],key_phrases1, key_phrases2, entity_name)
#
# tenure_yrs = tenure_test.get_tenure_length(sel_text)
# tenure_test.get_disclosure_flag(tenure_yrs)
#
# print (tenure_test.tenure_yrs)
# print (tenure_test.metric_flag)


