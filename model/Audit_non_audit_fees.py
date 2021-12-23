from General_ESG_Metric import GeneralESGMetric


class AuditFees(GeneralESGMetric):
    """ A class to extract the audit and non-audit fees from ESG reports

      Attributes:
            filename: pdf file
            company_name (string)
            metric_flag (string): representing the disclosure of an ESG metric in the PDF
            ('T' for True or 'F' for False)
            data (string): all text data from file as a single string
            audit_fees (int)
            non_audit_fees (int)
    """

    def __init__(self, filename, company_name, metric_flag, data, non_audit_flag):

        GeneralESGMetric.__init__(self, filename, company_name, metric_flag, data)
        self.audit_fee_flag = metric_flag
        self.non_audit_fee_flag = non_audit_flag
        # self.audit_fees = audit_fees #not computed yet
        # self.non_audit_fees = non_audit_fees

    def get_audit_nonaudit_fee_flag(self, doc):
        """
        A function to extract and identify whether auditor fees are mentioned in the ESG reports,
        then the fees are identified using the NER tagger which isolates numbers with currencies from other numbers.

        TODO: Distinguish between and extract the total, audit and non-audit fees returned and remove other values
        such as £100,000 or words.
        TODO: Improve the distinction between audit and non-audit fees. Currently they are grouped together.

        Args: All text in pdf file as a single string
        Returns: auditor fee flag (True/False)
        """

        if doc:
            fees = [ent.lemma_ for ent in doc if ent.ent_type_ == "MONEY"]
            #print("Fees:", fees)

            if fees:
                aud_fee_flag = 'T'  # assigning a T/F flag for binary classifier
                # just assuming if audit fees are disclosed, non-audit fees are disclosed as well
                nonaud_fee_flag = 'T'
            else:
                aud_fee_flag, nonaud_fee_flag = 'F', 'F'
        else:
            aud_fee_flag, nonaud_fee_flag = 'F', 'F'

        # displacy.render(doc, style="ent", jupyter=True)
        self.audit_fee_flag = aud_fee_flag
        self.non_audit_fee_flag = nonaud_fee_flag

        return



# testing
# fee_test = AuditFees('data_test_set/Unilever_Annual_Report_2020.pdf', [],[],[],[])
# fee_test.read_pdf_file()
#
# key_phrases1 = ['details of all audit fees', 'charged by the external auditor',
#                 # 'total fees paid to', 'total fees',
#                 'details of all fees charged by the external auditor',
#                 'audit fees payable', 'audit fee', 'audit-related work',
#                 'paid non-audit fees', 'non-audit services', 'non-audit',
#                 'non-audit related fees paid to the auditor',  # 'financial statements',
#                 'details of the fees paid to the External Auditing Firm',
#                 ]
# key_phrases2 = ('audit', 'non-audit', 'total')
#
# entity_name = 'AUD_FEES'
#
# doc, _,_,_ = fee_test.two_stage_sentence_selection([],key_phrases1, key_phrases2, entity_name)
# fee_test.get_audit_nonaudit_fee_flag(doc)
#
# print (fee_test.audit_fee_flag)
# print (fee_test.non_audit_fee_flag)
#
#
