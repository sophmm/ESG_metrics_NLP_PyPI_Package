import time
import glob,os
import pandas as pd

from General_ESG_Metric import select_sentences_using_re, create_truth_df, merge_predicted_and_true_metrics,\
    calculate_accuracy, calculate_evaluation_metrics_for_binary_metrics
from Auditor_name import AuditorName, create_Spacy_training_data_for_auditor_name, train_spacy_model
from Auditor_tenure import Tenure
from Audit_non_audit_fees import AuditFees
from Training_data_strings import patterns, NAME_TEXT

start_time = time.time()

# Create custom NER model
TRAINING_DATA = create_Spacy_training_data_for_auditor_name(patterns, NAME_TEXT)
custom_nlp_model = train_spacy_model(TRAINING_DATA, 30, blank_model=True) #performs better on blank model


#looping over all companies (one pdf file per company):

path = 'data_test_set/all/*' #directory of pdf files
truth_data = 'data_truth/Reference_unseen_test_data.xlsx' ##excel file of truth data for evaluation

all_auditor_flags = []
all_auditor_names = []
all_company_names = []
all_tenure_flags = []
all_tenure_lengths = []
all_aud_fee_flags = []
all_nonaud_fee_flags = []


for f in glob.glob(path):
    print (f)

    #get company name and auditor name:
    name_class = AuditorName(f, [], [], [], [])
    data = name_class.read_pdf_file()
    name_class.get_company_name()

    key_phrases = ['external auditor', 'statutory auditor', 'independent auditor', 'auditor', 'audit', 'for an on behalf of']
    sel_text = select_sentences_using_re(data, key_phrases)
    auditor_name = name_class.get_auditor_name(sel_text, custom_nlp_model)
    name_class.get_disclosure_flag(auditor_name)

    #get tenure:
    tenure_class = Tenure(f, [], [], [], [])

    key_phrases1 = ['external auditor', 'statutory auditor', 'independent auditor', 'audit tender',
                    'appointed as external auditor', 'reappointment','has been the Group’s auditor since',
                    'was the auditor', 'formal tender process', 'first appointed', 'competitive retender in',
                    'competitive tender process']
    key_phrases2 = ('appointed', 'reappointed', 'first appointed', 'since')

    _, _, _, sel_text = tenure_class.two_stage_sentence_selection(data, key_phrases1, key_phrases2, 'TENURE')
    tenure_yrs = tenure_class.get_tenure_length(sel_text)
    tenure_class.get_disclosure_flag(tenure_yrs)

    # get audit and non audit fees:
    fee_class = AuditFees(f, [], [], [], [])

    key_phrases1 = ['details of all audit fees', 'charged by the external auditor',
                    'details of all fees charged by the external auditor', 'audit fees payable', 'audit fee',
                    'audit-related work', 'paid non-audit fees', 'non-audit services', 'non-audit',
                    'non-audit related fees paid to the auditor', 'details of the fees paid to the External Auditing Firm']
    key_phrases2 = ('audit', 'non-audit', 'total')

    doc, _, _, _ = fee_class.two_stage_sentence_selection(data, key_phrases1, key_phrases2, 'AUD_FEES')
    fee_class.get_audit_nonaudit_fee_flag(doc)


    all_company_names.append(name_class.company)
    all_auditor_flags.append(name_class.metric_flag)
    all_auditor_names.append(name_class.auditor_name)
    all_tenure_flags.append(tenure_class.metric_flag)
    all_tenure_lengths.append(tenure_class.tenure_yrs)
    all_aud_fee_flags.append(fee_class.audit_fee_flag)
    all_nonaud_fee_flags.append(fee_class.non_audit_fee_flag)


print("--- %s seconds ---" % (time.time() - start_time))


## Converting to df and evaluating the accuracy over all companies:

data = {'Company': all_company_names,
        'Predicted Auditor Name Flag': all_auditor_flags,
        'Predicted Auditor Name': all_auditor_names,
        'Predicted Auditor Tenure Flag': all_tenure_flags,
        'Predicted Auditor Tenure': all_tenure_lengths,
        'Predicted Auditor Fee Flag': all_aud_fee_flags,
        'Predicted Non-Auditor Fee Flag': all_nonaud_fee_flags,

        }

df_predicted = pd.DataFrame(data)
df_predicted = df_predicted.sort_values(by=['Company'])  # sorting alphabetically

df_true = create_truth_df(truth_data)
df_full = merge_predicted_and_true_metrics(df_predicted, df_true)

predicted_cols = ['Predicted Auditor Name', 'Predicted Auditor Tenure', 'Predicted Auditor Tenure Flag',
                  'Predicted Auditor Fee Flag', 'Predicted Non-Auditor Fee Flag']

true_cols = ['Auditor name', 'Auditor tenure (years)', 'Is auditor tenure disclosed?',
             'Are audit fees disclosed?', 'Are non-audit fees disclosed?']

governance_metrics_binary = ([('Predicted Auditor Name Flag', 'Is auditor name disclosed?'),
                              ('Predicted Auditor Tenure Flag', 'Is auditor tenure disclosed?'),
                              ('Predicted Auditor Fee Flag', 'Are audit fees disclosed?'),
                              ('Predicted Non-Auditor Fee Flag', 'Are non-audit fees disclosed?')])



df_accuracy = calculate_accuracy(df_full, predicted_cols, true_cols)
df_evaluation_metrics = calculate_evaluation_metrics_for_binary_metrics(df_full, governance_metrics_binary)

print (df_accuracy)
print (df_evaluation_metrics)