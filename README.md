<
### ESGmetric_from_PDF

This package provides a proof-of-concept to show to extract specific sustainable investing Environmental, 
Societal and Governance (ESG) metrics from PDF files using Natural Language 
Processing (NLP). 

The code can be adapted to extract any ESG metric from text for example, SASB, Slavery Act etc., 
or it can be adapted to use your own training data to train the model on other documents.

## Table of Contents
1. [Introduction](#introduction)
2. [Objectives](#objectives)
3. [Getting Started](#getting_started)
4. [Authors](#authors)
5. [License](#license)

<a name="introduction"></a>
## Introduction

There is a growing demand for ESG products to analyse and rank performance metrics of companies
as investment managers must increasingly demonstrate due diligence. Currently relevant ESG 
metrics are manually extracted from annual report, which is very inefficient. As a team, 
we used NLP to automate extract of these metrics, increasing 
efficiency, reliablity, transparency and vertification. Increased transparency of 
corporate governance within an organisation greatly reduces investor risk. 

We focused on 3 specific governance metrics:

1. Auditor name
2. Current Auditor Tenure
3. Audit and non-audit Fees paid to the Auditor

Our objective approach provided a proof-of-concept for future metrics with
an accuracy of at least 78% (and f-score at least 0.86)


<a name="objectives"></a>
## Objectives

The data is composed of a series of annual reports (PDFs) from ~80 international companies,
e.g. Apple, Microsoft, Barclays, etc. 

1. We split the entire text up into words and sentences and searched for specific key phrases 
e.g. auditor, or external auditor, using a two-step filtering approach for improved accuracy.
The model below worked best with fewer sentences, so the 2 stage filtering was a quick and 
efficient way to narrow down to the right section we are interested in, instead of 
returning individual pages or sections. The low-level details e.g. capitalisation, 
punctuation, currency and stop words do matter so they were maintained in the text. 

2. We trained a custom Named Entity Recognition (NER) model to tag entities 
i.e. label specific words. The same idea can be used to train a different model 
to select anything (words/ values) you’re interested in from the text. 

3 Then we post-processed the output which further narrows down the list of names/ values
i.e. distinguish between present and past auditors.

4. The end result is a binary classification to distinguish whether the metric is 
disclosed, and if so, to extract the name or value.

If we had more time, we would have differentiated between the audit 
and non-audit fees, extracted values from tables or added sentiment analysis, 
for example to explore the integrity of the board members, potentially using a supervised
TF-IDF or bag of words approach.


<a name="getting_started"></a>
## Getting Started

The package is freely available on PyPi here: https://pypi.org/project/ESGmetric-from-PDF/0.1/

 `$ python3 -m venv ESGvenv`

 `$ source ESGvenv/bin/activate`

 `$ pip install ESGmetric_from_PDF

<a name="authors"></a>
## Authors

* [sophmm](https://github.com/sophmm)

<a name="license"></a>

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

