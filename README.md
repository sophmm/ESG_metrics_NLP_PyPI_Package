<
### ESGmetric_from_PDF

This package provides a proof-of-concept to show to extract specific ESG metrics 
(e.g. auditor name, tenure and fees) from PDF files using Natural Language 
Processing, to improve ESG scoring. 

The code can be adapted to extract any ESG metric from text for example environmental, societal or more governance metrics (SASB, Slavery Act etc.), or it can be adapted to use your own training data to train the model on other documents.
The package is freely available on PyPi here: https://pypi.org/project/ESGmetric-from-PDF/0.1/

## Table of Contents
1. [Introduction](#introduction)
2. [Objectives](#objectives)
3. [Getting Started](#getting_started)
    1. [Create Virtual Environment](#env)
4. [File Structure](#files)
5. [Discussion](#discussion)
    1. [Improvements](#improvements)
6. [Authors](#authors)
7. [License](#license)

<a name="introduction"></a>
## Introduction

##########
general context and why we chose this model/ filtering:
o	The low-level details e.g. capitalisation and punctuation & currency, stop words etc. do matter, so they maintained in the text. 
o	The NER model struggles with the entire body of text, so the 2 stage filtering is a quick & efficient way to narrow down to the right section we are interested in, instead of returning individual pages or sections.
o	I had to create a custom entity model as the existing entities didn’t recover the financial terms we were interested in
o	Then post-processing on the model results & re searches

##########

<a name="objectives"></a>
## Objectives

The data is composed of a series of annual reports (PDFs) from ~80 international companies,
e.g. Apple, Microsoft, Barclays, etc. 

The objectives are to extract 3 governance metrics from the reports using NLP:

1. Auditor name
2. Current Auditor Tenure
3. Audit and non-audit Fees paid to the Auditor

<a name="getting_started"></a>
## Getting Started

<a name="env"></a>
### Create Virtual Environment (Linux)

 `$ python3 -m venv ESGvenv`

 `$ source ESGvenv/bin/activate`

#######
add instructions for how to use package (and test it)
#######

<a name="discussion"></a>
## Discussion 

Possible improvements to the code are to differentiate between the audit 
and non-audit fees, extract values from tables or add sentiment analysis, 
for example to explore the integrity of the board members. 

o	Discuss how TF-IDF/ bag of words could be a supervised learning 
approach to extract board member profiles from the text (after manually 
labelling them)

<a name="authors"></a>
## Authors

* [sophmm](https://github.com/sophmm)

<a name="license"></a>

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

