---
title: "AI in Finance and Quantitative Analysis — Algorithmic Trading, Risk Management, Trading Bot and Event-Based Backtesting"
source: "https://web.ntpu.edu.tw/~myday/teaching/1111/AIFQA/1111AIFQA10_AI_in_Finance_and_Quantitative_Analysis.pdf"
author: "Min-Yuh Day (NTPU)"
published: 2022-12-13
created: 2026-08-08
description: "Vorlesungsfolien 1111AIFQA10: Algorithmic Trading, Risk Management, Trading Bot, Event-Based Backtesting"
tags:
  - clippings
  - algo-trading
  - backtesting
---

Artificial Intelligence in Finance and Quantitative Analysis

Algorithmic Trading, Risk Management,
Trading Bot and Event-Based Backtesting

1111AIFQA10
MBA, IM, NTPU (M6132) (Fall 2022)
Tue 2, 3, 4 (9:10-12:00) (B8F40)

Min-Yuh Day, Ph.D,
Associate Professor
Institute of Information Management, National Taipei University
https://web.ntpu.edu.tw/~myday

https://meet.google.com/
paj-zhhj-mya

2022-12-13

1

Syllabus

Week    Date    Subject/Topics

1   2022/09/13   Introduction to Artificial Intelligence in Finance and

Quantitative Analysis

2   2022/09/20   AI in FinTech: Metaverse, Web3, DeFi, NFT,

Financial Services Innovation and Applications

3   2022/09/27   Investing Psychology and Behavioral Finance

4   2022/10/04   Event Studies in Finance

5   2022/10/11   Case Study on AI in Finance and Quantitative Analysis I

6   2022/10/18   Finance Theory

2

Syllabus

Week    Date    Subject/Topics

7   2022/10/25   Data-Driven Finance

8   2022/11/01   Midterm Project Report

9   2022/11/08   Financial Econometrics and Machine Learning

10   2022/11/15   AI-First Finance

11   2022/11/22   Deep Learning in Finance;

Reinforcement Learning in Finance

12   2022/11/29   Case Study on AI in Finance and Quantitative Analysis II

3

Syllabus

Week    Date    Subject/Topics

13   2022/12/06   Industry Practices of AI in Finance and Quantitative

Analysis

14   2022/12/13   Algorithmic Trading; Risk Management;
Trading Bot and Event-Based Backtesting

15   2022/12/20   Final Project Report I

16   2022/12/27   Final Project Report II

17   2023/01/03   Self-learning

18   2023/01/10   Self-learning

4

Algorithmic Trading
Risk Management
Trading Bot
Event-Based Backtesting

5

Outline

• Algorithmic Trading
• Risk Management
• Trading Bot
• Event-Based Backtesting

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

6

Deep learning for
financial applications:
A survey
Applied Soft Computing (2020)

Source:
Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep
learning for financial applications: A survey."
Applied Soft Computing (2020): 106384.

7

Financial
time series forecasting with
deep learning:
A systematic literature review:
2005–2019
Applied Soft Computing (2020)

Source:
Omer Berat Sezer, Mehmet Ugur Gudelek, and Ahmet Murat Ozbayoglu (2020),
"Financial time series forecasting with deep learning: A systematic literature review:
2005–2019." Applied Soft Computing 90 (2020): 106181.

8

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Subtopic

Data set

Period

Feature set

Method

Performance criteria

Env.

Improving trading

S&P500, KOSPI, HSI,

1987–2017

200-days stock price

Deep Q-Learning and

decisions

and EuroStoxx50

DMLP

Total profit,

Correlation

[193]

Identifying Top

Forums data

2004–2013

Sentences and

keywords

Recursive neural

tensor networks

Precision, recall,

f-measure

[195]

Predicting Social Ins.

Taiwan’s National

2008–2014

Insured’s id,

RNN

Accuracy, total error

Python

Payment Behavior

Pension Insurance

area-code, gender,

etc.

[199]

Speedup

1991–2014

Price data

DNN

–

45 CME listed

commodity and FX

futures

Stocks in NYSE,

NASDAQ or AMEX

exchanges

1970–2017

16 fundamental

DMLP, LFM

features from balance

sheet

MSE, Compound

annual return, SR

20

Table 15

Art.

[47]

Other financial applications.

Sellers In

Underground

Economy

[200]

Forecasting

Fundamentals

[201]

[202]

Predicting Bank
Telemarketing

Corporate
Performance
Prediction

–

–

–

–

–

–

Phone calls of bank
marketing data

2008–2010

16 finance-related
attributes

Deep learning for financial applications:
Topics

22 pharmaceutical
companies data in US
stock market

11 financial and 4
patent indicator

2000–2015

RBM, DBN

CNN

Accuracy

RMSE, profit

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.
Fig. 8. The histogram of publication count in topics.

9

First and foremost, we clustered the various topics within the

application areas. However, since it is a natural extension of its

financial applications research and presented them in Fig. 8. A

shallow counterpart MLP, it has a longer history than the other

quick glance at the figure shows us financial text mining and

DL models.

algorithmic trading are the top two fields that the researchers

CNN started getting more attention lately since most of the

most worked on followed by risk assessment, sentiment analysis,

implementations appeared within the past 3 years. Careful anal-

portfolio management and fraud detection, respectively. The re-

ysis of CNN papers indicates that a recent trend of representing

sults indicate most of the papers were published within the past

financial data with a 2-D image view in order to utilize CNN

3 years implying the domain is very hot and actively studied.

is growing. Hence CNN based models might overpass the other

When the papers were clustered by the DL model type as

models in the future. It actually passed DMLP for the past 3 years.

presented in Fig. 9, we observe the dominance of RNN, DMLP

Furthermore, we attempted to provide more details about

and CNN over the remaining models, which might be expected,

associations between the DL models and the financial application

since these models are the most commonly preferred ones in

areas. Fig. 10 gives the distribution of the models for the research

general DL implementations. Meanwhile, RNN is a general um-

areas through a model-topic heatmap. Since most of the papers

brella model which has several versions including LSTM, GRU, etc.

had multiple DL models, the amount of models is more than

Within the RNN choice, most of the models actually belonged

the number of covered papers. The results indicate the broad

to LSTM, which is very popular in time series forecasting or

acceptance of RNN, DMLP and CNN models in almost all financial

regression problems. It is also used quite often in algorithmic

application areas.

trading. More than 70% of the RNN papers consisted of LSTM

We also wanted to elaborate on the particular feature se-

models.

lections for each financial application area to see if we could

Meanwhile, DMLP generally fits well for classification prob-

spot any pattern. Fig. 11 gives the distribution of the features

lems; hence it is a common choice for most of the financial

for the research areas through a feature-topic heatmap. Unlike

Deep learning for financial applications:
Deep Learning Models

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

21

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Fig. 9. The histogram of publication count in model types.

10

the heatmap, we see similarities with the feature-topic associa-

tions. However, this time, we had three main clusters of dataset

types, the first one being the temporal datasets like Stock, Index,

ETF, Cryptocurrency, Forex and Commodity price datasets, and

the second one being the text-based datasets like News, Tweets,

Microblogs and Financial Reports, and the last one being the

datasets that had both numeric and textual components like Con-

sumer Data, Credit Data and Financial Reports from companies or

analysts. As far as the dataset vs. application area associations are

concerned, these three main clusters were distributed as follows:

Stock, Index, Cryptocurrency, ETF datasets were used almost in

every application area except Risk Assessment and Fraud Detec-

tion which had less of temporal properties. Meanwhile, Credit

Data, Financial Reports and Consumer Data were particularly

used by these two application areas, namely Risk Assessment

and Fraud Detection. Lastly, pure text based datasets like news,

tweets, microblogs were preferred by Financial Sentiment Analy-

sis and Financial Text Mining studies. However, as was the case in

the feature-topic associations, temporal datasets like stock, ETF,

Index price datasets were also used with these studies since some

of them were tied with algorithmic trading models.

Fig. 10. Topic-model heatmap.

6. Discussion and open issues

the model-topic heatmap, in this case, we saw a distinction

between the associations. Even though price data and technical

indicators have been very popular for most of the research areas

that are involved with time series forecasting, like algorithmic

trading, portfolio management, financial sentiment analysis and

financial text mining, the studies that had more significant spatial

characteristics like risk assessment and fraud detection did not

depend much on these temporal features. One other noteworthy

difference came up with the adaptation of text related features.

Highly text-based applications like financial sentiment analysis,

financial text mining, risk assessment and fraud detection pre-

ferred to use features like text (extracted from tweets, news or

financial data) and sentiments during their model development

and implementation. However, the temporal characteristics of

the financial time series data were also important for financial

sentiment analysis and financial text mining, since a significant

portion of these models were integrated into algorithmic trading

systems.

After reviewing all the publications based on the selected cri-

teria explained in the previous section, we wanted to provide our

findings of the current state-of-the-art situation. Our discussions

are categorized by the DL models and implementation topics.

6.1. Discussions on DL models

It is possible to claim that LSTM is the dominant DL model

that is preferred by most researchers, due to its well-established

structure for financial time series data forecasting. Most of the fi-

nancial implementations have time-varying data representations

requiring regression-type approaches which fits very well for

LSTM and its derivatives due to their easy adaptations to the

problems. As long as the temporal nature of the financial data

remains, LSTM and its related family models will maintain their

popularities.

Meanwhile, CNN based models started getting more traction

among researchers in the last two years. Unlike LSTM, CNN works

better for classification problems and is more suitable for either

Fig. 12 elaborates on the distribution of the dataset types for

non-time varying or static data representations. However, since

the research areas through a dataset-topic heatmap. If we analyze

most financial data is time-varying, under normal circumstances,

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

21

Deep learning for financial applications:
Topic-Model Heatmap

Fig. 9. The histogram of publication count in model types.

the heatmap, we see similarities with the feature-topic associa-
tions. However, this time, we had three main clusters of dataset
types, the first one being the temporal datasets like Stock, Index,
ETF, Cryptocurrency, Forex and Commodity price datasets, and
the second one being the text-based datasets like News, Tweets,
Microblogs and Financial Reports, and the last one being the
datasets that had both numeric and textual components like Con-
sumer Data, Credit Data and Financial Reports from companies or
analysts. As far as the dataset vs. application area associations are
concerned, these three main clusters were distributed as follows:
Stock, Index, Cryptocurrency, ETF datasets were used almost in
every application area except Risk Assessment and Fraud Detec-
tion which had less of temporal properties. Meanwhile, Credit
Data, Financial Reports and Consumer Data were particularly
used by these two application areas, namely Risk Assessment
and Fraud Detection. Lastly, pure text based datasets like news,
tweets, microblogs were preferred by Financial Sentiment Analy-
sis and Financial Text Mining studies. However, as was the case in
the feature-topic associations, temporal datasets like stock, ETF,
Index price datasets were also used with these studies since some
of them were tied with algorithmic trading models.

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Fig. 10. Topic-model heatmap.

6. Discussion and open issues

11

the model-topic heatmap, in this case, we saw a distinction

between the associations. Even though price data and technical

indicators have been very popular for most of the research areas

that are involved with time series forecasting, like algorithmic

trading, portfolio management, financial sentiment analysis and

financial text mining, the studies that had more significant spatial

characteristics like risk assessment and fraud detection did not

depend much on these temporal features. One other noteworthy

difference came up with the adaptation of text related features.

Highly text-based applications like financial sentiment analysis,

financial text mining, risk assessment and fraud detection pre-

ferred to use features like text (extracted from tweets, news or

financial data) and sentiments during their model development

and implementation. However, the temporal characteristics of

the financial time series data were also important for financial

sentiment analysis and financial text mining, since a significant

portion of these models were integrated into algorithmic trading

systems.

After reviewing all the publications based on the selected cri-

teria explained in the previous section, we wanted to provide our

findings of the current state-of-the-art situation. Our discussions

are categorized by the DL models and implementation topics.

6.1. Discussions on DL models

It is possible to claim that LSTM is the dominant DL model

that is preferred by most researchers, due to its well-established

structure for financial time series data forecasting. Most of the fi-

nancial implementations have time-varying data representations

requiring regression-type approaches which fits very well for

LSTM and its derivatives due to their easy adaptations to the

problems. As long as the temporal nature of the financial data

remains, LSTM and its related family models will maintain their

popularities.

Meanwhile, CNN based models started getting more traction

among researchers in the last two years. Unlike LSTM, CNN works

better for classification problems and is more suitable for either

Fig. 12 elaborates on the distribution of the dataset types for

non-time varying or static data representations. However, since

the research areas through a dataset-topic heatmap. If we analyze

most financial data is time-varying, under normal circumstances,

Deep learning for financial applications:
Topic-Feature Heatmap

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

22

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Fig. 11. Topic-feature heatmap.

12

Fig. 12. Topic-dataset heatmap.

CNN is not the natural choice for financial applications. However,

Careful analyses of the reviews indicate in most of the papers

in some independent studies, the researchers performed an inno-

hybrid models are preferred over native models for better ac-

vative transformation of 1-D time-varying financial data into 2-D

complishments. A lot of researchers configure the topologies and

mostly stationary image-like data to be able to utilize the power

network parameters for achieving higher performance. However,

of CNN through adaptive filtering and implicit dimensionality

there is also the danger of creating more complex hybrid models

reduction. This novel approach seems working remarkably well

that are not easy to build, and their interpretation also might be

in complex financial patterns regardless of the application area.

difficult.

In the future, more examples of such implementations might be

Through the performance evaluation results, it is possible to

more common; only time will tell.

claim that in general terms, DL models outperform ML coun-

Another model that has a rising interest is DRL based im-

terparts when working on the same problems. DL models also

plementations; in particular, the ones coupled with agent-based

have the advantage of being able to work on larger amount of

modeling. Even though algorithmic trading is the most preferred

data. With the growing expansion of open-source DL libraries

implementation area for such models, it is possible to develop the

and frameworks, DL model building and development process is

working structures for any problem type.

easier than ever.

22

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Deep learning for financial applications:
Topic-Dataset Heatmap

Fig. 11. Topic-feature heatmap.

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Fig. 12. Topic-dataset heatmap.

13

CNN is not the natural choice for financial applications. However,

Careful analyses of the reviews indicate in most of the papers

in some independent studies, the researchers performed an inno-

hybrid models are preferred over native models for better ac-

vative transformation of 1-D time-varying financial data into 2-D

complishments. A lot of researchers configure the topologies and

mostly stationary image-like data to be able to utilize the power

network parameters for achieving higher performance. However,

of CNN through adaptive filtering and implicit dimensionality

there is also the danger of creating more complex hybrid models

reduction. This novel approach seems working remarkably well

that are not easy to build, and their interpretation also might be

in complex financial patterns regardless of the application area.

difficult.

In the future, more examples of such implementations might be

Through the performance evaluation results, it is possible to

more common; only time will tell.

claim that in general terms, DL models outperform ML coun-

Another model that has a rising interest is DRL based im-

terparts when working on the same problems. DL models also

plementations; in particular, the ones coupled with agent-based

have the advantage of being able to work on larger amount of

modeling. Even though algorithmic trading is the most preferred

data. With the growing expansion of open-source DL libraries

implementation area for such models, it is possible to develop the

and frameworks, DL model building and development process is

working structures for any problem type.

easier than ever.

6

Deep learning for financial applications:
Algo-trading applications embedded with time series forecasting models

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Table 1
Algo-trading applications embedded with time series forecasting models.

Art.

Data set

Period

Feature set

Method

[33]

[34]

GarantiBank in BIST,
Turkey

2016

CSI300, Nifty50, HSI,
Nikkei 225, S&P500, DJIA

2010–2016

OCHLV, Spread,
Volatility,
Turnover, etc.

OCHLV, Technical
Indicators

[35]

Chinese Stocks

2007–2017

OCHLV

PLR, Graves LSTM

WT, Stacked
autoencoders,
LSTM

CNN + LSTM

Performance
criteria

MSE, RMSE, MAE,
RSE, Correlation
R-square

MAPE, Correlation
coefficient,
THEIL-U

Annualized Return,
Mxm Retracement

50 stocks from NYSE

2007–2016

Price data

SFM

MSE

[36]

[37]

[38]

The LOB of 5 stocks of
Finnish Stock Market

2010

FI-2010 dataset:
bid/ask and
volume

WMTR, MDA

300 stocks from SZSE,
Commodity

2014–2015

Price data

FDDR, DMLP+RL

[39]

S&P500 Index

1989–2005

Price data, Volume

LSTM

[40]

[41]

[42]

Stock of National Bank
of Greece (ETE).

Chinese stock-IF-IH-IC
contract

Singapore Stock Market
Index

2009–2014

2016–2017

2010–2017

FTSE100, DJIA,
GDAX, NIKKEI225,
EUR/USD, Gold

Decisions for price
change

OCHL of last 10
days of Index

[43]

GBP/USD

2017

Price data

[44]

[45]

Commodity, FX future,
ETF

USD/GBP, S&P500,
FTSE100, oil, gold

1991–2014

Price Data

DMLP

2016

Price data

AE + CNN

Accuracy,
Precision, Recall,
F1-Score

Profit, return, SR,
profit-loss curves

Return, STD, SR,
Accuracy

Return, volatility,
SR, Accuracy

RMSE, MAPE,
Profit, SR

SR, downside
deviation ratio,
total profit

SR, capability
ratio, return

SR, % volatility,
avg return/trans,
rate of return

MODRL+LSTM

Profit and loss, SR

GASVR, LSTM

DMLP

Reinforcement
Learning + LSTM +
NES

Environment

Spark

–

Python

–

–

Keras

Python,
TensorFlow, Keras,
R, H2O

Tensorflow

–

–

Python, Keras,
Tensorflow

C++, Python

H2O

14

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
MA, BOLL, the
[46]
Computing (2020): 106384.
CRIX returns,
Euribor interest

Bitcoin, Dash, Ripple,
Monero, Litecoin,
Dogecoin, Nxt, Namecoin

Accuracy,
F1-measure

Python,
Tensorflow

LSTM, RNN, DMLP

2014–2017

[47]

S&P500, KOSPI, HSI, and

1987–2017

200-days stock

Deep Q-Learning,

EuroStoxx50

price

DMLP

[48]

Stocks in the S&P500

1990–2015

Price data

DMLP, GBT, RF

[49]

Fundamental and

–

CNN

–

Technical Data, Economic

Data

Total profit,

Correlation

Mean return,

MDD, Calmar ratio

–

–

H2O

rates, OCHLV

Fundamental ,

technical and

market

information

3.8. Other deep structures

4. Financial applications

The DL models are not limited to the ones mentioned in

the previous subsections. Some of the other well-known struc-

tures that exist in the literature are Deep Reinforcement Learn-

ing (DRL), Generative Adversarial Networks (GANs), Capsule Net-

works, Deep Gaussian Processes (DGPs). Meanwhile, we have not

encountered any noteworthy academic or industrial publication

on financial applications using these models so far, with the

exception of DRL which started getting attention lately. However,

that does not imply that these models do not fit well with the

financial domain. On the contrary, they offer great potentials for

researchers and practitioners participating in finance and deep

learning community who are willing to go the extra mile to come

up with novel solutions.

Since research for model developments in DL is ongoing, new

structures keep on coming. However, the aforementioned models

and their variations currently cover almost all of the published

There are a lot of financial applications of soft computing in

the literature. DL has been studied in most of them, although,

some opportunities still exist in a number of fields.

Throughout this section, we categorized the implementation

areas and presented them in separate subsections. Besides, in

each subsection we tabulated the representative models, datasets,

features of the relevant studies in order to provide as much

information as possible in the limited space.

In addition, we tried to elaborate on the preferred model, data

and feature choices for each financial application area separately

in the subsections. Our focus was to identify the dominant mod-

els, features and data types that standout for each application

area and very briefly explain the reasons behind those particular

choices. To provide an overall snapshot view, we accumulated

the corresponding model, feature and dataset associations cou-

work. Next section will provide details about the implementation

pled with the financial application areas within three separate

areas along with the preferred DL models.

heatmaps (Figs. 10–12) that are presented in Section 5.

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Algo-trading applications embedded with time series forecasting models.

Art.

Data set

Period

Feature set

Method

[33]

GarantiBank in BIST,

2016

PLR, Graves LSTM

Turkey

OCHLV, Spread,

Volatility,

Turnover, etc.

[34]

CSI300, Nifty50, HSI,

2010–2016

OCHLV, Technical

Nikkei 225, S&P500, DJIA

Indicators

WT, Stacked

autoencoders,

LSTM

CNN + LSTM

[35]

Chinese Stocks

2007–2017

OCHLV

Python

50 stocks from NYSE

2007–2016

Price data

SFM

MSE

The LOB of 5 stocks of

Finnish Stock Market

Commodity

2010

FI-2010 dataset:

WMTR, MDA

bid/ask and

volume

[38]

300 stocks from SZSE,

2014–2015

Price data

FDDR, DMLP+RL

Keras

[39]

S&P500 Index

1989–2005

Price data, Volume

LSTM

Return, STD, SR,

Python,

Performance

criteria

MSE, RMSE, MAE,

RSE, Correlation

R-square

MAPE, Correlation

coefficient,

THEIL-U

Annualized Return,

Mxm Retracement

Accuracy,

Precision, Recall,

F1-Score

Profit, return, SR,

profit-loss curves

Accuracy

SR, Accuracy

[40]

Stock of National Bank

2009–2014

FTSE100, DJIA,

GASVR, LSTM

Return, volatility,

Tensorflow

of Greece (ETE).

GDAX, NIKKEI225,

EUR/USD, Gold

[41]

Chinese stock-IF-IH-IC

2016–2017

Decisions for price

MODRL+LSTM

Profit and loss, SR

contract

change

6

Table 1

[36]

[37]

[42]

2010–2017

DMLP

Singapore Stock Market
Index

OCHL of last 10
days of Index

RMSE, MAPE,
Profit, SR

[43]

GBP/USD

6

Deep learning for financial applications:
SR, downside
deviation ratio,
A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384
total profit
Algo-trading applications embedded with time series forecasting models

Reinforcement
Learning + LSTM +
NES

Price data

2017

[44]
Table 1
Algo-trading applications embedded with time series forecasting models.

Commodity, FX future,
ETF

1991–2014

Price Data

DMLP

[45]
Art.

[33]
[46]

[34]

[47]

[35]
[48]

[36]
[49]
[37]

[38]

USD/GBP, S&P500,
Data set
FTSE100, oil, gold

GarantiBank in BIST,
Bitcoin, Dash, Ripple,
Turkey
Monero, Litecoin,
Dogecoin, Nxt, Namecoin
CSI300, Nifty50, HSI,
Nikkei 225, S&P500, DJIA
S&P500, KOSPI, HSI, and
EuroStoxx50
Chinese Stocks
Stocks in the S&P500

50 stocks from NYSE
Fundamental and
The LOB of 5 stocks of
Technical Data, Economic
Finnish Stock Market
Data

2016
Period

Price data
Feature set

AE + CNN
Method

2016
2014–2017

2010–2016

1987–2017

2007–2017
1990–2015

2007–2016
–
2010

OCHLV, Spread,
MA, BOLL, the
Volatility,
CRIX returns,
Turnover, etc.
Euribor interest
OCHLV, Technical
rates, OCHLV
Indicators
200-days stock
price
OCHLV
Price data

Price data
Fundamental ,
FI-2010 dataset:
technical and
bid/ask and
market
volume
information

PLR, Graves LSTM
LSTM, RNN, DMLP

WT, Stacked
autoencoders,
Deep Q-Learning,
LSTM
DMLP
CNN + LSTM
DMLP, GBT, RF

SFM
CNN
WMTR, MDA

300 stocks from SZSE,
Commodity

3.8. Other deep structures

[39]

S&P500 Index

2014–2015

Price data

FDDR, DMLP+RL

1989–2005

Price data, Volume

4. Financial applications

LSTM

SR, capability
ratio, return

SR, % volatility,
Performance
avg return/trans,
criteria
rate of return
MSE, RMSE, MAE,
Accuracy,
RSE, Correlation
F1-measure
R-square

MAPE, Correlation
coefficient,
Total profit,
THEIL-U
Correlation
Annualized Return,
Mean return,
Mxm Retracement
MDD, Calmar ratio
MSE
–
Accuracy,
Precision, Recall,
F1-Score

Profit, return, SR,
profit-loss curves

Return, STD, SR,
Accuracy

TensorFlow, Keras,

R, H2O

Environment

Spark

–

–

–

–

–

Python, Keras,
Tensorflow

C++, Python

H2O
Environment

Spark
Python,
Tensorflow

–

–

Python
H2O

–
–
–

Keras

Python,
TensorFlow, Keras,
R, H2O

There are a lot of financial applications of soft computing in
the literature. DL has been studied in most of them, although,
Return, volatility,
SR, Accuracy
some opportunities still exist in a number of fields.

GASVR, LSTM

Tensorflow

[40]

Stock of National Bank
of Greece (ETE).

The DL models are not limited to the ones mentioned in
the previous subsections. Some of the other well-known struc-
FTSE100, DJIA,
tures that exist in the literature are Deep Reinforcement Learn-
GDAX, NIKKEI225,
ing (DRL), Generative Adversarial Networks (GANs), Capsule Net-
EUR/USD, Gold
works, Deep Gaussian Processes (DGPs). Meanwhile, we have not
encountered any noteworthy academic or industrial publication
on financial applications using these models so far, with the

Chinese stock-IF-IH-IC
contract

2009–2014

2016–2017

[41]

Throughout this section, we categorized the implementation
Profit and loss, SR
Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
areas and presented them in separate subsections. Besides, in
15
Computing (2020): 106384.
each subsection we tabulated the representative models, datasets,

Decisions for price
change

MODRL+LSTM

–

[42]

Singapore Stock Market

2010–2017

OCHL of last 10

DMLP

exception of DRL which started getting attention lately. However,

days of Index

Index

that does not imply that these models do not fit well with the

Price data

GBP/USD

2017

[43]

financial domain. On the contrary, they offer great potentials for

researchers and practitioners participating in finance and deep

learning community who are willing to go the extra mile to come

Commodity, FX future,

1991–2014

Price Data

[44]

up with novel solutions.

ETF

[45]

Since research for model developments in DL is ongoing, new

USD/GBP, S&P500,

Price data

2016

structures keep on coming. However, the aforementioned models

FTSE100, oil, gold

and their variations currently cover almost all of the published

[46]

work. Next section will provide details about the implementation

Bitcoin, Dash, Ripple,

MA, BOLL, the

2014–2017

areas along with the preferred DL models.

Monero, Litecoin,

Dogecoin, Nxt, Namecoin

CRIX returns,

Euribor interest

rates, OCHLV

RMSE, MAPE,

Profit, SR

SR, downside

deviation ratio,

features of the relevant studies in order to provide as much

–

information as possible in the limited space.

Python, Keras,

Tensorflow

Reinforcement

Learning + LSTM +

In addition, we tried to elaborate on the preferred model, data

and feature choices for each financial application area separately

total profit

NES

in the subsections. Our focus was to identify the dominant mod-

SR, capability

C++, Python

DMLP

els, features and data types that standout for each application

ratio, return

area and very briefly explain the reasons behind those particular

SR, % volatility,

AE + CNN

H2O

choices. To provide an overall snapshot view, we accumulated

avg return/trans,

the corresponding model, feature and dataset associations cou-

rate of return

pled with the financial application areas within three separate

LSTM, RNN, DMLP

Accuracy,

Python,

heatmaps (Figs. 10–12) that are presented in Section 5.

F1-measure

Tensorflow

[47]

S&P500, KOSPI, HSI, and

1987–2017

200-days stock

Deep Q-Learning,

EuroStoxx50

price

DMLP

[48]

Stocks in the S&P500

1990–2015

Price data

DMLP, GBT, RF

[49]

Fundamental and

–

CNN

–

Technical Data, Economic

Data

Fundamental ,

technical and

market

information

Total profit,

Correlation

Mean return,

MDD, Calmar ratio

–

–

H2O

3.8. Other deep structures

4. Financial applications

The DL models are not limited to the ones mentioned in

the previous subsections. Some of the other well-known struc-

tures that exist in the literature are Deep Reinforcement Learn-

ing (DRL), Generative Adversarial Networks (GANs), Capsule Net-

works, Deep Gaussian Processes (DGPs). Meanwhile, we have not

encountered any noteworthy academic or industrial publication

on financial applications using these models so far, with the

exception of DRL which started getting attention lately. However,

that does not imply that these models do not fit well with the

financial domain. On the contrary, they offer great potentials for

researchers and practitioners participating in finance and deep

learning community who are willing to go the extra mile to come

up with novel solutions.

Since research for model developments in DL is ongoing, new

structures keep on coming. However, the aforementioned models

and their variations currently cover almost all of the published

There are a lot of financial applications of soft computing in

the literature. DL has been studied in most of them, although,

some opportunities still exist in a number of fields.

Throughout this section, we categorized the implementation

areas and presented them in separate subsections. Besides, in

each subsection we tabulated the representative models, datasets,

features of the relevant studies in order to provide as much

information as possible in the limited space.

In addition, we tried to elaborate on the preferred model, data

and feature choices for each financial application area separately

in the subsections. Our focus was to identify the dominant mod-

els, features and data types that standout for each application

area and very briefly explain the reasons behind those particular

choices. To provide an overall snapshot view, we accumulated

the corresponding model, feature and dataset associations cou-

work. Next section will provide details about the implementation

pled with the financial application areas within three separate

areas along with the preferred DL models.

heatmaps (Figs. 10–12) that are presented in Section 5.

Deep learning for financial applications:
Classification (buy–sell signal, or trend detection) based algo-trading models

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

7

Table 2
Classification (buy–sell signal, or trend detection) based algo-trading models.

Art.

Data set

Period

Feature set

Method

[51]

Stocks in Dow30

1997–2017

RSI

DMLP with genetic
algorithm

Performance
criteria

Environment

Annualized return

Spark MLlib, Java

[52]

SPY ETF, 10 stocks from
S&P500

2014–2016

Price data

[53]

Dow30 stocks

2012–2016

[54]

[55]

High-frequency record of
all orders

2014–2017

Nasdaq Nordic (Kesko
Oyj, Outokumpu Oyj,
Sampo, Rautaruukki,
Wartsila Oyj)

2010

[56]

17 ETFs

2000–2016

[57]

Stocks in Dow30 and 9
Top Volume ETFs

1997–2017

Close data and
several technical
indicators

Price data, record
of all orders,
transactions

Price and volume
data in LOB

Price data,
technical
indicators

Price data,
technical
indicators

[58]

FTSE100

2000–2017

Price data

[59]

[60]

Nasdaq Nordic (Kesko
Oyj, Outokumpu Oyj,
Sampo, Rautaruukki,
Wartsila Oyj)

Borsa Istanbul 100
Stocks

2010

2011–2015

Price, Volume
data, 10 orders of
the LOB

75 technical
indicators and
OCHLV

[61]

ETFs and Dow30

1997–2007

Price data

FFNN

LSTM

LSTM

LSTM

CNN

CNN with feature
imaging

CAE

CNN

CNN

CNN with feature
imaging

RL, DMLP, Genetic
Algorithm

Cumulative gain

Accuracy

Accuracy

Precision, Recall,
F1-score, Cohen’s
k

Accuracy, MSE,
Profit, AUROC

Recall, precision,
F1-score,
annualized return

TR, SR, MDD,
mean return

Precision, Recall,
F1-score, Cohen’s
k

MatConvNet,
Matlab

Python, Keras,
Tensorflow, TALIB

–

–

Keras, Tensorflow

Python, Keras,
Tensorflow, Java

–

Theano, Scikit
learn, Python

Accuracy

Keras

Annualized return

Keras, Tensorflow

Learning and
genetic algorithm
error

Missed
opportunities,
false alarms ratio

–

–

[62]

8 experimental assets
from bond/derivative
market

[63]

10 stocks from S&P500

–

–

[64]

London Stock Exchange

2007–2008

Asset prices data

Stock Prices

TDNN, RNN, PNN

Limit order book
state, trades,
buy/sell orders,
order deletions

CNN

Accuracy, kappa

Caffe

[65]

Cryptocurrencies, Bitcoin

2014–2017

Price data

CNN, RNN, LSTM

Accumulative
portfolio value,
MDD, SR

–

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Also, the readers should note that there were some overlaps
between different implementation areas for some papers. There

As a result, Algo-trading models based on DL also started getting
attention.

16

were two main reasons for that: In some papers, multiple prob-

lems were addressed separately, for e.g. text mining was studied

for feature extraction, then algorithmic trading was implemented.

For some other cases, the paper might fit directly into multiple

implementation areas due to the survey structure, for e.g. cryp-

tocurrency portfolio management. In such cases we included the

papers in all of the relevant subsections creating some overlaps.

Some of the existing study areas can be grouped as follows:

4.1. Algorithmic trading

Algorithmic trading (or Algo-trading) is defined as buy–sell

decisions made solely by algorithmic models. These decisions can

be based on some simple rules, mathematical models, optimized

processes, or as in the case of machine/deep learning, highly com-

plex function approximation techniques. With the introduction of

Most of the Algo-trading applications are coupled with price

prediction models for market timing purposes. As a result, a

majority of the price or trend forecasting models that trigger

buy–sell signals based on their prediction are also considered as

Algo-trading systems. However, there are also some studies that

propose stand-alone Algo-trading models focused on the dynam-

ics of the transaction itself by optimizing trading parameters such

as bid–ask spread, analysis of limit order book, position-sizing,

etc. High Frequency Trading (HFT) researchers are particularly

interested in this area. Hence, DL models also started appearing

in HFT studies.

Before diving into the DL implementations, it would be bene-

ficial to briefly mention about the existing ML surveys on Algo-

trading. Hu et al. [75] reviewed the implementations of various

EAs on Algorithmic Trading Models. Since financial time series

forecasting is highly coupled with algorithmic trading, there are

a number of ML survey papers focused on Algo-trading models

electronic online trading platforms and frameworks, algorithmic

based on forecasting. The interested readers can refer to [1] for

trading took over the finance industry in the last two decades.

more information.

8

Deep learning for financial applications:
Stand-alone and/or other algorithmic models

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Table 3
Stand-alone and/or other algorithmic models.

Art.

Data set

Period

Feature set

Method

[66]

[67]

[68]

DAX, FTSE100, call/put
options

Taiwan Stock Index
Futures, Mini Index
Futures

Energy-Sector/
Company-Centric Tweets
in S&P500

1991–1998

Price data

2012–2014

Price data to
image

2015–2016

Text and Price
data

Markov model,
RNN

Visualization
method + CNN

LSTM, RNN, GRU

[69]

CME FIX message

2016

Limit order book,
time-stamp, price
data

RNN

[70]

[71]

[72]

[73]

Taiwan stock index
futures (TAIFEX)

2017

Price data

Stocks from S&P500

2010–2016

OCHLV

News from NowNews,
AppleDaily, LTN,
MoneyDJ for 18 stocks

489 stocks from S&P500
and NASDAQ-100

2013–2014

Text, Sentiment

2014–2015

Limit Order Book

[74]

Experimental dataset

–

Price data

Agent based RL
with CNN
pre-trained

DCNL

DMLP

Spatial neural
network

DRL with CNN,
LSTM, GRU, DMLP

Performance
criteria

Ewa-measure, iv,
daily profits’ mean
and std

Accumulated
profits,accuracy

Return, SR,
precision, recall,
accuracy

Precision, recall,
F1-measure

Environment

–

–

Python, Tweepy
API

Python,
TensorFlow, R

Accuracy

–

PCC, DTW, VWL

Pytorch

Return

Cross entropy
error

Mean profit

Python,
Tensorflow

NVIDIA’s cuDNN

Python

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

As far as the DL research is concerned, Tables 1, 2, and 3
present the past and current status of algo-trading studies based

Forex or cryptocurrency trading was implemented in some
studies. In [43], agent inspired trading using deep (recurrent)

17

on DL models. The papers are distributed to these tables as

reinforcement learning and LSTM was implemented and tested

follows: Table 1 has the particular algorithmic trading implemen-

on the trading of GBP/USD. In [44], DMLP was implemented for

tations that are embedded with time series forecasting models,

the prediction of commodities and FX trading prices. Korczak

whereas Table 2 is focused on classification based (buy–sell Sig-

et al. [45] implemented a forex trading (GBP/PLN) model using

nal, or Trend Detection) algo-trading models. Finally, Table 3

several different input parameters on a multi-agent-based trading

presents stand-alone studies or other algorithmic trading mod-

environment. One of the agents used CNN for prediction and

els (pairs trading, arbitrage, etc.) that do not fit into the above

outperformed all other models.

categorization criteria.

On the cryptocurrency side, Spilak et al. [46] used several cryp-

Most of the Algo-trading studies were concentrated on the

tocurrencies to construct a dynamic portfolio using LSTM, RNN,

prediction of stock or index prices. Meanwhile, LSTM was the

DMLP methods. In a versatile study, Jeong et al. [47] combined

most preferred DL model in these implementations. In [33], mar-

deep Q-learning and DMLP to implement price forecasting and

ket microstructures based trade indicators were used as the input

they intended to solve three separate problems: Increasing profit

into RNN with Graves LSTM to perform the price prediction for

in a market, prediction of the number of shares to trade, and

algorithmic stock trading. Bao et al. [34] used technical indicators

preventing overfitting with insufficient financial data.

as the input into Wavelet Transforms (WT), LSTM and Stacked

In [51], technical analysis indicator’s (Relative Strength Index

Autoencoders (SAEs) for the forecasting of stock prices. In [35],

(RSI)) buy & sell limits were optimized with GA which was used

CNN and LSTM model structures were implemented together

for buy–sell signals. After optimization, DMLP was also used for

(CNN was used for stock selection, LSTM was used for price

function approximation. In [52], the authors combined deep Fully

prediction).

Connected Neural Network (FNN) with a selective trade strategy

Using a different model, Zhang et al. [36] proposed a novel

unit to predict the next price. In [53], the crossover and Moving

State Frequency Memory (SFM) recurrent network for stock price

Average Convergence and Divergence (MACD) signals were used

prediction with multiple frequency trading patterns and achieved

to predict the trend of the Dow 30 stocks’ prices. Sirignano

better prediction and trading performances. In an HFT trad-

et al. [54] proposed a novel method that used limit order book

ing system, Tran et al. [37] developed a DL model that im-

flow and history information for the determination of the stock

plements price change forecasting through mid-price prediction

movements using LSTM model. Tsantekidis et al. [55] also used

using high-frequency limit order book data with tensor represen-

limit order book time series data and LSTM method for the trend

tation. In [38], the authors used Fuzzy Deep Direct Reinforcement

prediction.

Learning (FDDR) for stock price prediction and trading signal

Several studies focused on utilizing CNN based models due

generation.

to their success in image classification problems. However, in

For index prediction, the following studies are noteworthy.

order to do that, the financial input data needed to be trans-

In [39], the price prediction of S&P500 index using LSTM was

formed into images which required some creative preprocessing.

implemented. Mourelatos et al. [40] compared the performance

Gudelek et al. [56] converted time series of price data to 2-

of LSTM and GA with a SVR (GASVR) for Greek Stock Exchange

dimensional images using technical analysis and classified them

Index prediction. Si et al. [41] implemented Chinese intraday

with deep CNN. Similarly, Sezer et al. [57] also proposed a novel

futures market trading model with DRL and LSTM. Yong et al. [42]

technique that converts financial time series data that consisted

used DMLP method and Open,Close,High, Low (OCHL) of the time

of technical analysis indicator outputs to 2-dimensional images

series index data to predict Singapore Stock Market index data.

and classified these images using CNN to determine the trading

10

Deep learning for financial applications:
Credit scoring or classification studies

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Table 4
Credit scoring or classification studies.

Art.

Data set

Period

Feature set

Method

[77]

The XR 14 CDS contracts

2016

[78]

[79]

[80]

[81]

[82]

[83]

German, Japanese credit
datasets

Credit data from Kaggle

Australian, German
credit data

German, Australian
credit dataset

Consumer credit data
from Chinese finance
company

Credit approval dataset
by UCI Machine Learning
repo

–

–

–

–

–

–

Recovery rate,
spreads, sector
and region

Personal financial
variables

Personal financial
variables

Personal financial
variables

Personal financial
variables

Relief algorithm
chose the 50 most
important features

UCI credit
approval dataset

DBN+RBM

SVM + DBN

DMLP

GP + AE as
Boosted DMLP

DCNN, DMLP

CNN + Relief

Rectifier, Tanh,
Maxout DL

Performance
criteria

AUROC, FN, FP,
Accuracy

Weighted-
accuracy, TP,
TN

Accuracy, TP, TN,
G-mean

FP

Accuracy,
False/Missed alarm

AUROC, K-s
statistic, Accuracy

Env.

WEKA

–

–

Python,
Scikit-learn

–

Keras

–

AWS EC2, H2O, R

Table 5
Financial distress, bankruptcy, bank risk, mortgage risk, crisis forecasting studies.

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

18

Art.

Data set

Period

Feature set

Method

Performance

criteria

Env.

966 french firms

–

Financial ratios

RBM+SVM

Precision, Recall

883 BHC from EDGAR

2006–2017

Tokens, weighted

sentiment polarity,

leverage and ROA

CNN, LSTM, SVM,

Accuracy,

RF

Precision, Recall,

Keras, Python,

Scikit-learn

2007–2014

Word, sentence

DMLP +NLP

preprocess

F1-score

Relative

usefulness,

F1-score

[87]

Event dataset on

2007–2014

Text, sentence

Sentence vector +

Usefulness,

DFFN

F1-score, AUROC

[88]

News from Reuters,

2007–2014

doc2vec + NN

Relative usefulness

Doc2vec

Financial ratios

and news text

[89]

1976–2017

Macro economic

CGAN, MVN, MV-t,

RMSE, Log

variables and bank

performances

LSTM, VAR,

FE-QAR

likelihood, Loan

loss rate

[90]

Financial statements of

2002–2006

Financial ratios

DBN

DBN

Recall, Precision,

F1-score, FP, FN

[91]

Stock returns of

2001–2011

Price data

Accuracy

Python, Theano

2002–2016

Financial ratios

CNN

F1-score, AUROC

[93]

Mortgage dataset with

1995–2014

Mortgage related

DMLP

2012–2016

Personal financial

CNN

Negative average

log-likelihood

AWS

Accuracy,

Sensitivity,

Specificity, AUROC

[95]

Private brokerage

–

CNN, LSTM

F1-Score

Keras, Tensorflow

[84]

[85]

[86]

[92]

[94]

The event data set for

large European banks,

news articles from

Reuters

European banks, news

from Reuters

fundamental data

Macro/Micro economic

variables, Bank charac-

teristics/performance

variables from BHC

French companies

American publicly-traded

companies from CRSP

Financial statements of

several companies from

Japanese stock market

local and national

economic factors

Mortgage data from

Norwegian financial

service group, DNB

company’s real data of

risky transactions

combined to create a

new one

[96]

Several datasets

1996–2017

Logit, CART, RF,

SVM, NN,

XGBoost, DMLP

AUROC, KS,

G-mean, likelihood

ratio, DP, BA, WBA

features

variables

250 features:

order details, etc.

Index data,

10-year Bond

yield, exchange

rates,

–

–

–

–

–

–

–

R

(majority) instances, finally they used an ensemble of DMLPs

assessment rules in order to generate good or bad credit cases.

combining each subspace model. In [80], credit scoring was per-

In another study, Neagoe et al. [81] classified credit scores using

formed using a SAE network and GP model to create credit

various DMLP and deep CNN networks. In a different study [82],

10

Table 4

[79]

[80]

[81]

[82]

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Credit scoring or classification studies.

Art.

Data set

Period

Feature set

Method

[77]

The XR 14 CDS contracts

2016

DBN+RBM

[78]

German, Japanese credit

Personal financial

SVM + DBN

Credit data from Kaggle

Personal financial

DMLP

Recovery rate,

spreads, sector

and region

variables

variables

Personal financial

variables

variables

datasets

Australian, German

credit data

German, Australian

credit dataset

Personal financial

DCNN, DMLP

Accuracy,

Performance

criteria

AUROC, FN, FP,

Accuracy

Weighted-

accuracy, TP,

Accuracy, TP, TN,

G-mean

TN

FP

False/Missed alarm

AUROC, K-s
statistic, Accuracy

Env.

WEKA

–

–

–

Python,

Scikit-learn

Keras

GP + AE as

Boosted DMLP

CNN + Relief

–

–

–

–

–

Consumer credit data
from Chinese finance
company

Relief algorithm
chose the 50 most
important features

[83]

Deep learning for financial applications:
Financial distress, bankruptcy, bank risk, mortgage risk, crisis forecasting studies.

Credit approval dataset
by UCI Machine Learning
repo

UCI credit
approval dataset

Rectifier, Tanh,
Maxout DL

AWS EC2, H2O, R

–

–

Table 5
Financial distress, bankruptcy, bank risk, mortgage risk, crisis forecasting studies.

Art.

Data set

Period

Feature set

Method

Performance
criteria

Env.

966 french firms

–

Financial ratios

RBM+SVM

Precision, Recall

–

883 BHC from EDGAR

2006–2017

Tokens, weighted
sentiment polarity,
leverage and ROA

2007–2014

Word, sentence

CNN, LSTM, SVM,
RF

DMLP +NLP
preprocess

Accuracy,
Precision, Recall,
F1-score

Relative
usefulness,
F1-score

[84]

[85]

[86]

[87]

[88]

[89]

[90]

[91]

[92]

[93]

[94]

[95]

[96]

The event data set for
large European banks,
news articles from
Reuters

Event dataset on
European banks, news
from Reuters

News from Reuters,
fundamental data

Macro/Micro economic
variables, Bank charac-
teristics/performance
variables from BHC

Financial statements of
French companies

Stock returns of
American publicly-traded
companies from CRSP

Financial statements of
several companies from
Japanese stock market

Mortgage dataset with
local and national
economic factors

Mortgage data from
Norwegian financial
service group, DNB

Private brokerage
company’s real data of
risky transactions

Several datasets
combined to create a
new one

Keras, Python,
Scikit-learn

–

–

–

–

2007–2014

Text, sentence

Sentence vector +
DFFN

Usefulness,
F1-score, AUROC

2007–2014

1976–2017

Financial ratios
and news text

Macro economic
variables and bank
performances

CGAN, MVN, MV-t,
LSTM, VAR,
FE-QAR

RMSE, Log
likelihood, Loan
loss rate

doc2vec + NN

Relative usefulness

Doc2vec

2002–2006

Financial ratios

2001–2011

Price data

DBN

DBN

Recall, Precision,
F1-score, FP, FN

Accuracy

Python, Theano

2002–2016

Financial ratios

CNN

F1-score, AUROC

–

1995–2014

Mortgage related
features

2012–2016

Personal financial
variables

–

250 features:
order details, etc.

1996–2017

Index data,
10-year Bond
yield, exchange
rates,

DMLP

CNN

Negative average
log-likelihood

Accuracy,
Sensitivity,
Specificity, AUROC

AWS

–

CNN, LSTM

F1-Score

Keras, Tensorflow

Logit, CART, RF,
SVM, NN,
XGBoost, DMLP

AUROC, KS,
G-mean, likelihood
ratio, DP, BA, WBA

R

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

assessment rules in order to generate good or bad credit cases.

(majority) instances, finally they used an ensemble of DMLPs

combining each subspace model. In [80], credit scoring was per-

In another study, Neagoe et al. [81] classified credit scores using

formed using a SAE network and GP model to create credit

various DMLP and deep CNN networks. In a different study [82],

19

Deep learning for financial applications:
Fraud detection studies

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

12

Table 6
Fraud detection studies.

Art.

Data set

Period

Feature set

Method

[114]

Debit card transactions
by a local Indonesia
bank

2016–2017

Financial
transaction
amount on several
time periods

CNN,
Stacked-LSTM,
CNN-LSTM

Performance
criteria

AUROC

Env.

–

LSTM, GRU

Accuracy

Keras

[117]

Transactions made with
credit cards by European
cardholders

2013

Personal financial
variables to PCA

DMLP, RF

Recall, Precision,
Accuracy

[115]

Credit card transactions
from retail banking

2017

[116]

Card purchases’
transactions

2014–2015

Transaction
variables and
several derived
features

Probability of
fraud per
currency/origin
country, other
fraud related
features

[118]

Credit-card transactions

2015

[119]

[120]

[121]

[122]

[123]

[124]

Databases of foreign
trade of the Secretariat
of Federal Revenue of
Brazil

Chamber of Deputies
open data, Companies
data from Secretariat of
Federal Revenue of Brazil

Real-world data for
automobile insurance
company labeled as
fradulent

Transactions from a
giant online payment
platform

Financial transactions

Empirical data from
Greek firms

2014

2009–2017

–

2006

–

–

Transaction and
bank features

8 Features:
Foreign Trade, Tax,
Transactions,
Employees,
Invoices, etc

21 features:
Brazilian State
expense, party
name, Type of
expense, etc.

Car, insurance and
accident related
features

Personal financial
variables

DMLP

AUROC

LSTM

AE

AUROC

MSE

Keras, Scikit-learn

H2O, R

Deep
Autoencoders

MSE, RMSE

H2O, R

–

–

–

–

–

Torch

DMLP + LDA

TP, FP, Accuracy,
Precision, F1-score

GBDT+DMLP

AUROC

Transaction data

–

LSTM

DQL

t-SNE

Revenue

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

4.3.1. Model, feature and dataset selections for fraud detection

best-performing assets for a given period. As a result, there are a
lot of EA models that were developed for this purpose. Metaxiotis

Fraud Detection, more or less, has similar domain character-

20

4.4. Portfolio management

istics when compared with Risk Assessment, hence the corre-

et al. [126] surveyed the MOEAs implemented solely on the

sponding model, feature and dataset selections were also highly

portfolio optimization problem. However, some DL researchers

correlated. As a result, the underlying dynamics that are valid for

managed to configure it as a learning model and obtained supe-

Risk Assessment are also applicable to Fraud Detection. Maybe,

rior performances. Since Robo-advisory for portfolio management

the only notable difference we can mention was the preferrence

is on the rise, these DL implementations have the potential to

of the consumer data as the most preferred dataset instead of the

have a far greater impact on the financial industry in the near

credit data for Fraud Detection.

future. Table 7 presents the portfolio management DL models and

Full distribution of models, features and datasets used by the

summarizes their achievements.

fraud detection implementations are presented in Figs. 10–12.

There are a number of stock selection implementations.

Takeuchi et al. [127] classified the stocks in two classes, low

momentum and high momentum depending on their expected

return. They used a deep RBM encoder-classifier network and

achieved high returns. Similarly, in [128], stocks were evaluated

Portfolio Management is the process of choosing various assets

within the portfolio for a predetermined period. As seen in other

against their benchmark index to classify if they would outper-

financial applications, slightly different versions of this problem

form or underperform using DMLP, then based on the predictions,

exist, even though the underlying motivation is the same. In

adjusted the portfolio allocation weights for the stocks for en-

general, Portfolio Management covers the following closely re-

hanced indexing. In [129], an ML framework including DMLP was

lated areas: Portfolio Optimization, Portfolio Selection, Portfolio

constructed and the stock selection problem was implemented.

Allocation. Sometimes, these terms are used interchangeably. Li

Portfolio selection and smart indexing were the main focuses

et al. [125] reviewed the online portfolio selection studies using

of [130] and [131] using AE and LSTM networks. Lin et al. [132]

various rule-based or ML models.

used the Elman network for optimal portfolio selection by pre-

Portfolio Management is actually an optimization problem,

dicting the stock returns for t+1 and then constructing the opti-

identifying the best possible course-of-action for selecting the

mum portfolio according to the returns. Meanwhile, Maknickiene

Deep learning for financial applications:
Portfolio management studies

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

13

Table 7
Portfolio management studies.

Art.

[65]

[127]

Data set

Period

Feature set

Method

Cryptocurrencies, Bitcoin

2014–2017

Price data

CNN, RNN, LSTM

Stocks from NYSE,
AMEX, NASDAQ

1965–2009

Price data

[128]

20 stocks from S&P500

2012–2015

[129]

Chinese stock data

2012–2013

Technical
indicators

Technical,
fundamental data

[130]

[131]

[132]

[133]

[134]

Top 5 companies in
S&P500

–

Price data and
Financial ratios

IBB biotechnology index,
stocks

2012–2016

Price data

Taiwans stock market

FOREX (EUR/USD, etc.),
Gold

Stocks in NYSE, AMEX,
NASDAQ, TAQ intraday
trade

–

2013

Price data

Price data

1993–2017

Price, 15 firm
characteristics

Autoencoder +
RBM

DMLP

Logistic
Regression, RF,
DMLP

LSTM,
Auto-encoding,
Smart indexing

Auto-encoding,
Calibrating,
Validating,
Verifying

Elman RNN

Evolino RNN

Performance
criteria

Accumulative
portfolio value,
MDD, SR

Accuracy,
confusion matrix

Accuracy

AUC, accuracy,
precision, recall,
f1, tpr, fpr

CAGR

Returns

MSE, return

Return

LSTM+DMLP

Monthly return, SR

[135]

S&P500

1985–2006

monthly and daily
log-returns

DBN+MLP

[136]

10 stocks in S&P500

1997–2016

OCHLV, Price data

RNN, LSTM, GRU

[137]

[138]

[139]

Analyst reports on the
TSE and Osaka Exchange

Stocks from
Chinese/American stock
market

Hedge fund monthly
return data

2016–2018

Text

2015–2018

OCHLV,
Fundamental data

1996–2015

Return, SR, STD,
Skewness,
Kurtosis, Omega
ratio, Fund alpha

LSTM, CNN,
Bi-LSTM

DDPG, PPO

DMLP

[140]

12 most-volumed
cryptocurrency

2015–2016

Price data

CNN + RL

Validation, Test
Error

Accuracy, Monthly
return

Accuracy, R2

SR, MDD

Sharpe ratio,
Annual return,
Cum. return

SR, portfolio value,
MDD

Env.

–

–

Python, Scikit
Learn, Keras,
Theano

Keras, Tensorflow,
Python, Scikit
learn

–

–

–

Python

Python,Keras,
Tensorflow in
AWS

Theano, Python,
Matlab

Keras, Tensorflow

R, Python, MeCab

–

–

–

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

et al. [141] used Evolino RNN for portfolio selection and re-
turn prediction accordingly. The selected portfolio components
(stocks) were orthogonal in nature.

Cryptocurrency portfolio management also started getting at-
tention from DL researchers. In [140], portfolio management (al-
location and adjustment of weights) was implemented by CNN

21

In [134], through predicting the next month’s return, top to

and DRL on selected cryptocurrencies. Similarly, Jiang et al. [65]

be performed portfolios were constructed and good monthly

implemented cryptocurrency portfolio management (allocation)

returns were achieved with LSTM and LSTM-DMLP combined DL

based on 3 different proposed models, namely RNN, LSTM and

models. Similarly, Batres et al. [135] combined DBN and MLP for

CNN.

constructing a stock portfolio by predicting each stock’s monthly

log-return and choosing the only stocks that were expected to

4.4.1. Model, feature and dataset selections for portfolio manage-

perform better than the performance of the median stock. Lee

ment

et al. [136] compared 3 RNN models (S-RNN, LSTM, GRU) for stock

In some ways, portfolio management can be considered simi-

price prediction and then constructed a threshold-based portfolio

lar to algorithmic trading except the corresponding timeframes

with selecting the stocks according to the predictions. With a dif-

are very different. Algorithmic trading is implemented in rel-

ferent approach, Iwasaki et al. [137] used the analyst reports for

atively shorter durations, i.e. milliseconds to hours or days at

sentiment analyses through text mining and word embeddings

most, meanwhile the typical timeframes for portfolio manage-

and used the sentiment features as inputs to Deep Feedforward

ment are in the order of days, months or years. However, when

Neural Network (DFNN) model for the stock price prediction.

we compare the models, features and datasets that were used for

After that, different portfolio selections were implemented based

algorithmic trading studies, we saw, more or less, a very simi-

on the projected stock returns.

lar pattern for portfolio management. Meanwhile, even though

DRL was selected as the main DL model for [138]. Liang

spatial properties or features were almost nonexistent for algo-

et al. [138] used DRL for portfolio allocation by adjusting the

rithmic trading models, there were a few spatial features and

stocks weights using various RL models. Chen et al. [139] com-

datasets that were used for portfolio management studies. Since

pared different ML models (including DFFN) for hedge fund return

most portfolio managers rely on analyst reports for their alloca-

prediction and hedge fund selection. DL and RF models had the

tion decisions, it is logical that some DL models also use similar

best performance.

features or datasets for training.

Deep learning for financial applications:
Asset pricing and derivatives market studies

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

14

Table 8
Asset pricing and derivatives market studies.

Art.

Der. type

Data set

Period

Feature set

Method

[137]

Asset
pricing

[142]

Options

[143]

[144]

Futures,
Options

Equity
returns

Analyst reports on
the TSE and Osaka
Exchange

2016–2018

Text

Simulated a range of
call option prices

–

Price data, option
strike/maturity,
dividend/risk free
rates, volatility

LSTM, CNN,
Bi-LSTM

DMLP

Performance
criteria

Accuracy, R2

Env.

R, Python, MeCab

RMSE, the average
percentage pricing
error

Tensorflow

TAIEX Options

2017

OCHLV, fundamental
analysis, option price

DMLP, DMLP with
Black scholes

RMSE, MAE, MAPE

–

Returns in NYSE,
AMEX, NASDAQ

1975–2017

57 firm
characteristics

Fama–French
n-factor model DL

R2,RMSE

Tensorflow

Full distribution of models, features and datasets used by the
are presented in
implementations

portfolio management
Figs. 10–12.

4.5. Asset pricing and derivatives market (options, futures, forward
contracts)

options pricing, the price irregularities at the tail-ends for the
options, too many possibilities for complex formations result-
ing in too many potential features to consider, etc. Hence the
intrinsic dynamics are quite complex in the derivatives market.
Even though not many academic papers are published, one might
think the financial institutions and their quantitative strategy
development departments might be working on these products
without publishing their results. This is probably a valid concern,
meanwhile these firms may be reluctant to openly publish their

22

Accurate pricing or valuation of an asset is a fundamental
study area in finance. There are a vast number of ML models

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

developed for banks, corporates, real estate, derivative prod-

models to the public for business protection, so it might not be

ucts, etc. However, DL has not been applied to this particular

possible to find openly accessible studies on this topic as easy

field and there are some possible implementation areas that

as the other financial application areas. However, this is an ex-

DL models can assist the asset pricing researchers or valuation

citing area with tremendous opportunities for professionals and

experts. There were only a handful of studies that we were able

researchers, but the readers should carefully assess the rewards

to pinpoint within the DL and finance community. There are vast

and risks associated with the model development using these

opportunities in this field for future studies and publications.

highly volatile and often complex products.

Meanwhile, financial models based on derivative products is

Full distribution of models, features and datasets used by the

quite common. Options pricing, hedging strategy development,

derivatives market implementations are presented in Figs. 10–12.

financial engineering with options, futures, forward contracts are

among some of the studies that can benefit from developing

4.6. Cryptocurrency and blockchain studies

DL models. Some recent studies indicate that researchers started

showing interest in DL models that can provide solutions to this

In the last few years, cryptocurrencies have been very pop-

complex and challenging field. Table 8 summarizes these studies

ular due to their incredible price gain and loss within short

with their intended purposes.

periods. Even though price forecasting dominates the area of

Iwasaki et al. [137] used a DFNN model and the analyst reports

interest, some other studies also exist, such as cryptocurrency

for sentiment analyses to predict the stock prices. Different port-

Algo-trading models.

folio selection approaches were implemented after the prediction

Meanwhile, Blockchain is a new technology that provides a

of the stock prices. Culkin et al. [142] proposed a novel method

distributed decentralized ledger system that fits well with the

that used DMLP model to predict option prices by comparing their

cryptocurrency world. As a matter of fact, cryptocurrency and

results with Black & Scholes option pricing formula. Similarly, Hsu

blockchain are highly coupled, even though blockchain technol-

et al. [143] proposed a novel method that predicted TAIEX option

ogy has a much wider span for various implementation possibil-

prices using bid–ask spreads and Black & Scholes option price

ities that need to be studied. It is still in its early development

model parameters with 3-layer DMLP. In [144], characteristic fea-

phase, hence there is a lot of hype in its potentials.

tures such as Asset growth, Industry momentum, Market equity,

Some DL models have already appeared about cryptocurrency

Market Beta, etc. were used as inputs to a Fama–French n-factor

studies, mostly price prediction or trading systems. However, still

model DL to predict US equity returns in National Association

there is a lack of studies for blockchain research within the DL

of Securities Dealers Automated Quotations (NASDAQ), Ameri-

community. Given the attention that the underlying technology

can Stock Exchange (AMEX), New York Stock Exchange (NYSE)

has attracted, there is a great chance that some new studies will

indices.

start appearing in the near future. Table 9 tabulates the studies

for the cryptocurrency and blockchain research.

4.5.1. Model, feature and dataset selections for derivatives market

Chen et al. [145] proposed a blockchain transaction trace-

There are a lot of options studies with machine learning,

ability algorithm using Takagi–Sugeno fuzzy cognitive map and

mostly pricing and volatility estimation research. Meanwhile,

3-layer DMLP. Bitcoin data (Hash value, bitcoin address, pub-

when compared with the other areas of finance, this area can

lic/private key, digital signature, etc.) was used as the dataset. Nan

still be considered mostly untouched, since it did not attract

et al. [146] proposed a method for bitcoin mixing detection that

the researchers from a wider perspective. The other derivative

consisted of different stages: Constructing the Bitcoin transaction

products are even more scarce compared to the options. The

graph, implementing node embedding, detecting outliers through

trend still continues for the deep learning era.

AE. Lopes et al. [147] combined the opinion market and price pre-

There might be several reasons behind this scarcity of pub-

diction for cryptocurrency trading. Text mining combined with 2

lications for derivative products: Lack of openly available his-

models, CNN and LSTM were used to extract the opinion. Bitcoin,

toric data, the implicit ambiguity using the implied volatility for

Litecoin, StockTwits were used as the dataset. Open,Close,High,

Deep learning for financial applications:
Cryptocurrency and blockchain studies

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Table 9
Cryptocurrency and blockchain studies.

15

Art.

Data set

Period

Feature set

Method

[46]

Bitcoin, Dash, Ripple,
Monero, Litecoin,
Dogecoin, Nxt, Namecoin

2014–2017

LSTM, RNN, DMLP

MA, BOLL, the
CRIX daily returns,
Euribor interest
rates, OCHLV of
EURO/UK,
EURO/USD, US/JPY

[65]

Cryptocurrencies, Bitcoin

2014–2017

Price data

CNN

[140]

12 most-volumed
cryptocurrency

2015–2016

Price data

CNN + RL

[145]

Bitcoin data

2010–2017

[146]

Bitcoin data

2012, 2013, 2016

[147]

Bitcoin, Litecoin,
StockTwits

2015–2018

Hash value,
bitcoin address,
public/private key,
digital signature,
etc.

TransactionId,
input/output
Addresses,
timestamp

OCHLV, technical
indicators,
sentiment analysis

[148]

Bitcoin

2013–2016

Price data

Takagi–Sugeno
Fuzzy cognitive
maps

Graph embedding
using heuristic,
laplacian
eigen-map, deep
AE

CNN, LSTM, State
Frequency Model

Bayesian
optimized RNN,
LSTM

Performance
criteria

Accuracy,
F1-measure

Env.

Python,
Tensorflow

Accumulative
portfolio value,
MDD, SR

SR, portfolio value,
MDD

Analytical
hierarchy process

F1-score

–

–

–

MSE

Keras, Tensorflow

Sensitivity,
specificity,
precision,
accuracy, RMSE

Keras, Python,
Hyperas

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Low, Volume (OCHLV) of prices, technical indicators, and sen-
timent analysis were used as the feature set. In another study,

textual data. Nowadays there is broad interest in the sentiment
analysis for financial forecasting research using DL models. Ta-

Jiang et al. [65] presented a financial-model-free RL framework

ble 10 provides information about the sentiment analysis stud-

for the Cryptocurrency portfolio management that was based on

ies that are focused on financial forecasting and based on text

3 different proposed models, basic RNN, LSTM and CNN. In [140],

mining.

portfolio management was implemented by CNN and DRL on 12

In [150], technical analysis (MACD, Moving Average (MA),

most-volumed cryptocurrencies. Bitcoin, Ethereum, Bitcoin Cash

Directional Movement Index (DMI), Exponential Moving Average

and Digital Cash were used as the dataset. In addition, Spilak

(EMA), Triple Exponential Moving Average (TEMA), Momentum,

et al. [46] used 8 cryptocurrencies (Bitcoin, Dash, Ripple, Mon-

RSI, Commodity Channel Index (CCI), Stochastic Oscillator, Price

ero, Litecoin, Dogecoin, Nxt, Namecoin) to construct a dynamic

of Change (ROC)) and sentiment analysis (using social media)

portfolio using LSTM, RNN, DMLP methods. McNally et al. [148]

were used to predict the price of stocks. Shi et al. [151] pro-

compared Bayesian optimized RNN, LSTM and Autoregressive

posed a method that visually interpreted text-based DL models

Integrated Moving Average (ARIMA) to predict the bitcoin price

in predicting the stock price movements. They used the finan-

direction. Sensitivity, specificity, precision, accuracy, Root Mean

cial news from Reuters and Bloomberg. In [152], text mining

Square Error (RMSE) were used as the performance metrics.

and word embeddings were used to extract information from

the financial news from Reuters and Bloomberg to predict the

4.6.1. Model, feature and dataset selections for cryptocurrency and

stock price movements. In addition, in [153], the prices of index

blockchain studies

data and emotional data from text posts were used to predict

Since most of the cryptocurrency studies were focused on

the stock opening price of the next day. Wang [154] performed

cryptocurrency price forecasting or trading systems, the choice

classification and stock price prediction using text and price data.

of models and features are similar to the algotrading selections.

Das et al. [155] used Twitter sentiment data and stock price data

Meanwhile in some studies ( [145] and [146]) cryptocurrency

to predict the prices of Google, Microsoft and Apple stocks. Prosky

specific features were selected. Also, for the datasets, the price

et al. [156] performed sentiment, mood prediction using news

data of the most popular cryptocurrency coins were used.

from Reuters and used these sentiments for price prediction.

Full distribution of models, features and datasets used by the

Li et al. [157] used sentiment classification (neutral, positive,

cryptocurrency implementations are presented in Figs. 10–12.

negative) for the stock open or close price prediction with LSTM

4.7. Financial sentiment analysis and behavioral finance

achieved higher overall performance. Iwasaki et al. [137] used an-

(various models). They compared their results with SVM and

alyst reports for sentiment analysis through text mining and word

One of the most important components of behavioral finance

embeddings. They used the sentiment features as inputs to DFNN

is emotion or investor sentiment. Lately, advancements in text

model for price prediction. Finally, different portfolio selections

mining techniques opened up the possibilities for successful sen-

were implemented based on the projected stock returns.

timent extraction through social media feeds. There is a growing

In a different study, Huang et al. [158] used several models

interest in Financial Sentiment Analysis, especially for trend fore-

including Hidden Markov Model (HMM), DMLP and CNN using

casting and Algo-trading model development. Kearney et al. [149]

Twitter moods along with the financial price data for prediction of

surveyed ML-based financial sentiment analysis studies that use

the next day’s move (up or down). CNN achieved the best result.

23

16

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Deep learning for financial applications:
Financial sentiment studies coupled with text mining for forecasting

Table 10
Financial sentiment studies coupled with text mining for forecasting.

Art.

Data set

Period

Feature set

Method

[137]

[150]

[151]

[152]

Analyst reports on the
TSE and Osaka Exchange

Sina Weibo, Stock
market records

News from Reuters and
Bloomberg for S&P500
stocks

News from Reuters and
Bloomberg, Historical
stock security data

[153]

SCI prices

[154]

SCI prices

[155]

[156]

[157]

[158]

Stocks of Google,
Microsoft and Apple

30 DJIA stocks, S&P500,
DJI, news from Reuters

Stocks of CSI300 index,
OCHLV of CSI300 index

S&P500, NYSE
Composite, DJIA,
NASDAQ Composite

2016–2018

Text

2012–2015

2006–2015

Technical
indicators,
sentences

Financial news,
price data

LSTM, CNN,
Bi-LSTM

DRSE

Performance
criteria

Accuracy, R2

F1-score,
precision, recall,
accuracy, AUROC

Env.

R, Python, MeCab

Python

DeepClue

Accuracy

Dynet software

2006–2013

News, price data

DMLP

Accuracy

2008–2015

2013–2016

2016–2017

2002–2016

2009–2014

2009–2011

OCHL of change
rate, price

Text data and
Price data

Twitter sentiment
and stock prices

Price data and
features from
news articles

Sentiment Posts,
Price data

Twitter moods,
index data

Emotional Analysis
+ LSTM

MSE

LSTM

RNN

LSTM, NN, CNN
and word2vec

Naive Bayes +
LSTM

DNN, CNN

Accuracy,
F1-Measure

–

Python, Keras

Spark,
Flume,Twitter API,

Accuracy

VADER

Precision, Recall,
F1-score, Accuracy

Python, Keras

Error rate

Keras, Theano

–

–

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Even though financial sentiment is highly coupled with text

news, financial statements, disclosures, etc. through analyzing the

24

mining, we decided to represent those two topics in different

text context. There are a few ML surveys focused on text mining

subsections. The main reason for such a choice is not only the ex-

and news analytics. Among the noteworthy studies of such, Mitra

istence of some financial sentiment studies which do not directly

et al. [159] edited a book on news analytics in finance, whereas

depend on financial textual data (like [158]) but also the existence

Li et al. [160], Loughran et al. [161], Kumar et al. [162] surveyed

of some financial text mining studies that are not automatically

the studies of textual analysis of financial documents, news and

used for sentiment analysis which will be covered in Section 4.8.

corporate disclosures. It is worth to mention that there are also

some studies [163,164] of text mining for financial prediction

4.7.1. Model, feature and dataset selections for financial sentiment

models.

analysis

Previous section was focused on DL models using sentiment

Financial sentiment analysis is mostly used along with fi-

analysis specifically tailored for the financial forecasting imple-

nancial text mining and algotrading models. As a result, the

mentations, whereas this section will include DL studies that

model choices were highly correlated with the aforementioned

have text Mining without Sentiment Analysis for Forecasting

financial application areas. Meanwhile, even though the model

(Table 11), financial sentiment analysis coupled with text mining

choices were highly similar, there were significant differences

without forecasting intent (Table 12) and finally other text mining

in the feature and dataset choices. For the features, text re-

implementations (Table 13), respectively.

lated ones such as extracted text from various sources like mi-

Huynh et al. [165] used the financial news from Reuters,

croblogs, news, reports dominated the studies. Also some papers

Bloomberg and stock prices data to predict the stock move-

directly used the sentiment feature extracted through APIs. The

ments in the future. In [166], different event-types on Chinese

rest of the used features were similar to the algotrading features,

companies are classified based on a novel event-type pattern

like price data and technical indicators. For the datasets, news

classification algorithm. Besides, the stock prices were predicted

and tweet/microblog repositories were the most popular choices.

using additional inputs. Kraus et al. [167] implemented LSTM

However, stock and index datasets were also used. There were

with transfer learning using text mining through financial news

also some studies that used financial reports as their data sources.

and stock market data. Dang et al. [168] used Stock2Vec and Two-

Full distribution of models, features and datasets used by the

stream GRU (TGRU) models to generate the input data from the

financial sentiment analysis implementations are presented in

financial news and stock prices for classification.

Figs. 10–12.

4.8. Financial text mining

In [169], events were detected from Reuters and Bloomberg

news through text mining. The extracted information was used

for price prediction and stock trading with the CNN model. Vargas

et al. [170] used text mining and price prediction together for

With the rapid spreading of social media and real-time stream-

intraday directional movement estimation. Akita et al. [171] im-

ing news/tweets, instant text-based information retrieval became

plemented a method that used text mining and price prediction

available for financial model development. As a result, finan-

together for forecasting prices. Verma et al. [172] combined news

cial text mining studies became very popular in recent years.

data with financial data to classify the stock price movement. Bari

Even though some of these studies are directly interested in

et al. [68] used text mining for extracting information from the

the sentiment analysis through crowdsourcing, there are a lot of

tweets and news. In the method, time series models were used for

implementations that are interested in the content retrieval of

stock trade signal generation. In [173], a method that performed

17

25

Art.

[68]

[165]

[166]

[168]

[169]

[170]

[171]

[172]

[173]

Deep learning for financial applications:
Text mining studies without sentiment analysis for forecasting

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Table 11
Text mining studies without sentiment analysis for forecasting.

Data set

Period

Feature set

Method

Energy-Sector/
Company-Centric Tweets
in S&P500

News from Reuters,
Bloomberg

News from Sina.com,
ACE2005 Chinese corpus

2015–2016

Text and Price
data

RNN, KNN, SVR,
LinR

2006–2013

Financial news,
price data

2012–2016

A set of news text

[167]

CDAX stock market data

2010–2013

Apple, Airbus, Amazon
news from Reuters,
Bloomberg, S&P500 stock
prices

S&P500 Index, 15 stocks
in S&P500

2006–2013

2006–2013

S&P500 index news from
Reuters

2006–2013

10 stocks in Nikkei 225
and news

2001–2008

Financial news,
stock market data

Price data, news,
technical
indicators

News from
Reuters and
Bloomberg

Financial news
titles, Technical
indicators

Textual
information and
Stock prices

Performance
criteria

Return, SR,
precision, recall,
accuracy

Env.

Python, Tweepy
API

Bi-GRU

Accuracy

Python, Keras

Their unique
algorithm

LSTM

TGRU, stock2vec

Precision, Recall,
F1-score

MSE, RMSE, MAE,
Accuracy, AUC

Accuracy,
precision, AUROC

–

TensorFlow,
Theano, Python,
Scikit-Learn

Keras, Python

CNN

Accuracy, MCC

SI-RCNN (LSTM +
CNN)

Accuracy

Paragraph Vector
+ LSTM

Profit

–

–

–

–

NIFTY50 Index, NIFTY
Bank/Auto/IT/Energy
Index, News

2013–2017

Index data, news

LSTM

MCC, Accuracy

Price data, index data,
news, social media data

2015

[174]

HS300

2015–2017

Price data, news
from articles and
social media

Social media
news, price data

Coupled matrix
and tensor

Accuracy, MCC

Jieba

RNN-Boost with
LDA

Accuracy, MAE,
MAPE, RMSE

Python,
Scikit-learn

[175]

News and Chinese stock
data

Selected words in
Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
a news
Computing (2020): 106384.
Price data and

Accuracy, Annual
return

News, stock prices from

ELM, DLR, PCA,

2014–2017

Accuracy

Matlab

2001

HAN

–

[176]

TF-IDF from news

BELM, KELM, NN

[177]

TWSE index, 4 stocks in

2001–2017

Technical

CNN + LSTM

RMSE, Profit

Keras, Python,

TALIB

indicators, Price

data, News

[178]

Stock of Tsugami

2013

Price data

LSTM

RMSE

Keras, Tensorflow

[179]

News, Nikkei Stock

1999–2008

news, MACD

RNN, RBM+DBN

Accuracy, P-value

[180]

ISMIS 2017 Data Mining

–

Expert identifier,

LSTM + GRU +

Accuracy

[181]

2006–2013

Accuracy

[182]

APPL from S&P500 and

2011–2017

Input news,

Accuracy, F1-score

Tensorflow

Hong Kong Stock

Exchange

TWSE

Corporation

Average and 10-Nikkei

companies

Competition dataset

Reuters, Bloomberg

News, S&P500 price

news from Reuters

from Reuters and

Bloomberg

[183]

Nikkei225, S&P500, news

2001–2013

Stock price data

DGM

[184]

Stocks from S&P500

2006–2013

Text (news) and

Accuracy, MCC,

%profit

MAPE, RMSE

OCHLV, Technical

indicators

classes

News and

sentences

and news

Price data

FFNN

LSTM

CNN + LSTM,

CNN+SVM

LAR+News,

RF+News

–

–

–

–

–

information fusion from news and social media sources was

price direction classification using the financial news and stocks

proposed to predict the trend of the stocks.

prices. In [177], financial news data and word embedding with

In [174], social media news were used to predict the index

Word2vec were implemented to create the inputs for Recurrent

price and the index direction with RNN-Boost through Latent

CNN (RCNN) to predict the stock price.

Dirichlet Allocation (LDA) features. Hu et al. [175] proposed a

Minami et al. [178] proposed a method that predicted the

novel method that used text mining techniques and Hybrid At-

stock price with corporate action event information and macro-

tention Networks based on the financial news for forecasting

economic index data using LSTM. In [179], a novel method that

the trend of stocks. Li et al. [176] implemented intraday stock

used a combination of RBM, DBN and word embeddings to create

Art.

[174]
[68]

[175]

[165]
[176]

[166]

[177]
[167]

[178]
[168]

[179]

[169]
[180]

[170]
[181]

[182]
[171]

[183]
[172]

[184]
[173]

Table 11

Art.

[68]

[171]

[172]

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

17

Text mining studies without sentiment analysis for forecasting.

Data set

Period

Feature set

Method

2015–2016

Text and Price

RNN, KNN, SVR,

Python, Tweepy

data

LinR

[165]

News from Reuters,

2006–2013

Financial news,

Bi-GRU

Python, Keras

Bloomberg

price data

[166]

News from Sina.com,

2012–2016

A set of news text

Precision, Recall,

–

Their unique

algorithm

[167]

CDAX stock market data

2010–2013

Financial news,

LSTM

[168]

Apple, Airbus, Amazon

2006–2013

Price data, news,

TGRU, stock2vec

Accuracy,

Energy-Sector/

Company-Centric Tweets

in S&P500

ACE2005 Chinese corpus

news from Reuters,

Bloomberg, S&P500 stock

prices

in S&P500

Reuters

stock market data

technical

indicators

News from

Reuters and

Bloomberg

Financial news

titles, Technical

indicators

[169]

S&P500 Index, 15 stocks

2006–2013

CNN

Accuracy, MCC

[170]

S&P500 index news from

2006–2013

SI-RCNN (LSTM +

Accuracy

CNN)

Performance

criteria

Return, SR,

precision, recall,

accuracy

Accuracy

F1-score

MSE, RMSE, MAE,

Accuracy, AUC

precision, AUROC

Profit

Env.

API

–

–

–

TensorFlow,

Theano, Python,

Scikit-Learn

Keras, Python

2001–2008

10 stocks in Nikkei 225
and news

Textual
information and
Stock prices

Paragraph Vector
+ LSTM

Deep learning for financial applications:
Text mining studies without sentiment analysis for forecasting

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

NIFTY50 Index, NIFTY
Bank/Auto/IT/Energy
Index, News

Index data, news

MCC, Accuracy

2013–2017

LSTM

–

17

Table 11
[173]
Text mining studies without sentiment analysis for forecasting.

2015

Price data, index data,
news, social media data
Data set

HS300
Energy-Sector/
Company-Centric Tweets
in S&P500
News and Chinese stock
data
News from Reuters,
Bloomberg
News, stock prices from
Hong Kong Stock
News from Sina.com,
Exchange
ACE2005 Chinese corpus
TWSE index, 4 stocks in
CDAX stock market data
TWSE

Stock of Tsugami
Apple, Airbus, Amazon
Corporation
news from Reuters,
Bloomberg, S&P500 stock
News, Nikkei Stock
prices
Average and 10-Nikkei
companies
S&P500 Index, 15 stocks
in S&P500
ISMIS 2017 Data Mining
Competition dataset

S&P500 index news from
Reuters, Bloomberg
Reuters
News, S&P500 price

APPL from S&P500 and
10 stocks in Nikkei 225
news from Reuters
and news

Period

2015–2017
2015–2016

2014–2017

2006–2013
2001

2012–2016

2001–2017
2010–2013

2013
2006–2013

1999–2008

2006–2013
–

2006–2013
2006–2013

2011–2017
2001–2008

Price data, news
from articles and
Feature set
social media

Social media
Text and Price
news, price data
data
Selected words in
a news
Financial news,
price data
Price data and
TF-IDF from news
A set of news text

Technical
Financial news,
indicators, Price
stock market data
data, News

Price data
Price data, news,
technical
indicators
news, MACD

News from
Reuters and
Expert identifier,
Bloomberg
classes

Financial news
News and
titles, Technical
sentences
indicators
Input news,
Textual
OCHLV, Technical
information and
indicators
Stock prices
Stock price data
Index data, news
and news

Coupled matrix
and tensor
Method

RNN-Boost with
RNN, KNN, SVR,
LDA
LinR
HAN

Bi-GRU
ELM, DLR, PCA,
BELM, KELM, NN
Their unique
algorithm
CNN + LSTM
LSTM

LSTM
TGRU, stock2vec

RNN, RBM+DBN

CNN
LSTM + GRU +
FFNN

SI-RCNN (LSTM +
LSTM
CNN)

CNN + LSTM,
Paragraph Vector
CNN+SVM
+ LSTM

Accuracy, MCC

Performance
criteria
Accuracy, MAE,
Return, SR,
MAPE, RMSE
precision, recall,
accuracy
Accuracy, Annual
return
Accuracy
Accuracy

Precision, Recall,
F1-score
RMSE, Profit
MSE, RMSE, MAE,
Accuracy, AUC

RMSE
Accuracy,
precision, AUROC
Accuracy, P-value

Accuracy, MCC
Accuracy

Accuracy
Accuracy

Jieba

Env.

Python,
Python, Tweepy
Scikit-learn
API
–

Python, Keras
Matlab

–

Keras, Python,
TensorFlow,
TALIB
Theano, Python,
Scikit-Learn
Keras, Tensorflow
Keras, Python

–

–
–

–
–

Accuracy, F1-score
Profit

Tensorflow
–

2001–2013
2013–2017

Nikkei225, S&P500, news
NIFTY50 Index, NIFTY
from Reuters and
Bank/Auto/IT/Energy
Bloomberg
Index, News
Stocks from S&P500
Price data, index data,
news, social media data
Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Text (news) and
Price data, news
Price data
from articles and
social media

LAR+News,
Coupled matrix
RF+News
and tensor

Accuracy, MCC,
MCC, Accuracy
%profit

MAPE, RMSE
Accuracy, MCC

2006–2013
2015

DGM
LSTM

–
–

–
Jieba

information fusion from news and social media sources was

Social media

2015–2017

HS300

[174]

price direction classification using the financial news and stocks
Accuracy, MAE,

RNN-Boost with

Python,

proposed to predict the trend of the stocks.

news, price data

prices. In [177], financial news data and word embedding with

MAPE, RMSE

Scikit-learn

LDA

[175]

In [174], social media news were used to predict the index

News and Chinese stock

Selected words in

2014–2017

Word2vec were implemented to create the inputs for Recurrent

Accuracy, Annual

HAN

–

price and the index direction with RNN-Boost through Latent

a news

data

CNN (RCNN) to predict the stock price.

return

[176]

Dirichlet Allocation (LDA) features. Hu et al. [175] proposed a

News, stock prices from

Price data and

2001

ELM, DLR, PCA,

Minami et al. [178] proposed a method that predicted the

Accuracy

Matlab

novel method that used text mining techniques and Hybrid At-

stock price with corporate action event information and macro-

TF-IDF from news

BELM, KELM, NN

Hong Kong Stock

Exchange

tention Networks based on the financial news for forecasting

economic index data using LSTM. In [179], a novel method that

[177]

TWSE index, 4 stocks in

2001–2017

Technical

CNN + LSTM

RMSE, Profit

the trend of stocks. Li et al. [176] implemented intraday stock

used a combination of RBM, DBN and word embeddings to create

Keras, Python,

TALIB

TWSE

indicators, Price

data, News

[178]

Stock of Tsugami

2013

Price data

LSTM

RMSE

Keras, Tensorflow

[179]

News, Nikkei Stock

1999–2008

news, MACD

RNN, RBM+DBN

Accuracy, P-value

[180]

ISMIS 2017 Data Mining

–

Expert identifier,

LSTM + GRU +

Accuracy

[181]

2006–2013

Accuracy

[182]

APPL from S&P500 and

2011–2017

Input news,

Accuracy, F1-score

Tensorflow

Corporation

Average and 10-Nikkei

companies

Competition dataset

Reuters, Bloomberg

News, S&P500 price

news from Reuters

from Reuters and

Bloomberg

[183]

Nikkei225, S&P500, news

2001–2013

Stock price data

DGM

[184]

Stocks from S&P500

2006–2013

Text (news) and

Accuracy, MCC,

%profit

MAPE, RMSE

OCHLV, Technical

indicators

classes

News and

sentences

and news

Price data

FFNN

LSTM

CNN + LSTM,

CNN+SVM

LAR+News,

RF+News

–

–

–

–

–

information fusion from news and social media sources was

price direction classification using the financial news and stocks

proposed to predict the trend of the stocks.

prices. In [177], financial news data and word embedding with

In [174], social media news were used to predict the index

Word2vec were implemented to create the inputs for Recurrent

price and the index direction with RNN-Boost through Latent

CNN (RCNN) to predict the stock price.

Dirichlet Allocation (LDA) features. Hu et al. [175] proposed a

Minami et al. [178] proposed a method that predicted the

novel method that used text mining techniques and Hybrid At-

stock price with corporate action event information and macro-

tention Networks based on the financial news for forecasting

economic index data using LSTM. In [179], a novel method that

the trend of stocks. Li et al. [176] implemented intraday stock

used a combination of RBM, DBN and word embeddings to create

26

18

Deep learning for financial applications:
Financial sentiment studies coupled with text mining without forecasting

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Table 12
Financial sentiment studies coupled with text mining without forecasting.

Art.

[85]

[185]

[186]

[187]

[188]

[189]

Data set

Period

Feature set

Method

883 BHC from EDGAR

2006–2017

SemEval-2017 dataset,
financial text, news,
stock market data

Financial news from
Reuters

2017

2006–2015

Stock sentiment analysis
from StockTwits

2015

Sina Weibo, Stock
market records

2012–2015

Tokens, weighted
sentiment polarity,
leverage and ROA

Sentiments in
Tweets, News
headlines

Word vector,
Lexical and
Contextual input

StockTwits
messages

Technical
indicators,
sentences

CNN, LSTM, SVM,
Random Forest

Ensemble SVR,
CNN, LSTM, GRU

Targeted
dependency tree
LSTM

LSTM, Doc2Vec,
CNN

DRSE

Performance
criteria

Accuracy,
Precision, Recall,
F1-score

Cosine similarity
score, agreement
score, class score

Cumulative
abnormal return

Accuracy,
precision, recall,
f-measure, AUC

F1-score,
precision, recall,
accuracy, AUROC

News from NowNews,
AppleDaily, LTN,
MoneyDJ for 18 stocks

2013–2014

Text, Sentiment

LSTM, CNN

Return

Env.

Keras, Python,
Scikit-learn

Python, Keras,
Scikit Learn

–

–

Python

Python,
Tensorflow

[190]

StockTwits

2008–2016

Sentences,
StockTwits
messages

CNN, LSTM, GRU

MCC, WSURT

Keras, Tensorflow

[191]

[192]

Financial statements of
Japan companies

Twitter posts, news
headlines

–

–

[193]

Forums data

2004–2013

[194]

News from Financial
Times related US stocks

–

Sentences, text

DMLP

Sentences, text

Deep-FASP

Sentences and
keywords

Sentiment of news
headlines

Recursive neural
tensor networks

SVR, Bidirectional
LSTM

Precision, recall,
f-score

Accuracy, MSE, R2

Precision, recall,
f-measure

Cosine similarity

–

–

–

Python, Scikit
Learn, Keras,
Tensorflow

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

Table 13
Other text mining studies.

Data set

Period

Feature set

Method

Performance

Env.

27

News from NowNews,

2013–2014

Text, Sentiment

DMLP

2007–2014

Word, sentence

DMLP +NLP

preprocess

criteria

Return

Relative

usefulness,

F1-score

Art.

[72]

[86]

[88]

[123]

[195]

AppleDaily, LTN,

MoneyDJ for 18 stocks

The event data set for

large European banks,

news articles from

Reuters

European banks, news

from Reuters

News from Reuters,

fundamental data

automobile insurance

company labeled as

fradulent

Financial transactions

Taiwan’s National

Pension Insurance

–

–

[87]

Event dataset on

2007–2014

Text, sentence

Sentence vector +

Usefulness,

DFFN

F1-score, AUROC

[121]

Real-world data for

Car, insurance and

DMLP + LDA

TP, FP, Accuracy,

Precision, F1-score

2007–2014

Financial ratios

and news text

doc2vec + NN

Relative usefulness

Doc2vec

accident related

features

Transaction data

etc.

Sentences,

StockTwits

messages

2008–2014

Insured’s id,

area-code, gender,

LSTM

RNN

t-SNE

error

Accuracy, total

Python

[196]

StockTwits

2015–2016

Doc2vec, CNN

Accuracy,

precision, recall,

f-measure, AUC

Python,

Tensorflow

word vectors for RNN-RBM-DBN network was proposed to pre-

et al. [182] proposed a method that used word embeddings with

dict the stock prices. Buczkowski et al. [180] proposed a novel

word2Vec, technical analysis features and stock prices for price

method that used expert recommendations, ensemble of GRU and

prediction. In [183], Deep Neural Generative Model (DGM) with

LSTM for prediction of the prices.

news articles using Paragraph Vector algorithm was used for cre-

In [181] a novel method that used character-based neural

ation of the input vector to predict the stock prices. In [184], the

language model using financial news and LSTM was proposed. Liu

stock price data and word embeddings were used for stock price

Python,

Tensorflow

–

–

–

–

[190]

StockTwits

2008–2016

CNN, LSTM, GRU

MCC, WSURT

Keras, Tensorflow

18

Table 12

Art.

[85]

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Financial sentiment studies coupled with text mining without forecasting.

Data set

Period

Feature set

Method

883 BHC from EDGAR

2006–2017

[185]

SemEval-2017 dataset,

2017

[186]

Financial news from

2006–2015

CNN, LSTM, SVM,

Random Forest

Ensemble SVR,

CNN, LSTM, GRU

Tokens, weighted

sentiment polarity,

leverage and ROA

Sentiments in

Tweets, News

headlines

Word vector,

Lexical and

Contextual input

LSTM

Targeted

Cumulative

dependency tree

abnormal return

[187]

Stock sentiment analysis

2015

LSTM, Doc2Vec,

Accuracy,

[188]

Sina Weibo, Stock

2012–2015

CNN

DRSE

[189]

News from NowNews,

2013–2014

Text, Sentiment

LSTM, CNN

Return

financial text, news,

stock market data

Reuters

from StockTwits

market records

AppleDaily, LTN,

MoneyDJ for 18 stocks

StockTwits

messages

Technical

indicators,

sentences

Sentences,

StockTwits

messages

Performance

criteria

Accuracy,

Precision, Recall,

F1-score

Cosine similarity

score, agreement

score, class score

precision, recall,

f-measure, AUC

F1-score,

precision, recall,

accuracy, AUROC

Precision, recall,

f-score

Accuracy, MSE, R2

[191]

Financial statements of

Sentences, text

DMLP

[192]

Twitter posts, news

Sentences, text

Deep-FASP

Japan companies

headlines

–

–

[193]

Forums data

2004–2013

Sentences and

keywords

Recursive neural

tensor networks

Precision, recall,

f-measure

News from Financial
Times related US stocks

–

Sentiment of news
headlines

SVR, Bidirectional
LSTM

Deep learning for financial applications:
Other text mining studies

Cosine similarity

Table 13
Other text mining studies.

Data set

Period

Feature set

Method

2013–2014

Text, Sentiment

DMLP

2007–2014

Word, sentence

DMLP +NLP
preprocess

Performance
criteria

Return

Relative
usefulness,
F1-score

Env.

Keras, Python,

Scikit-learn

Python, Keras,

Scikit Learn

Python

Python,

Tensorflow

–

–

–

–

–

Python, Scikit
Learn, Keras,
Tensorflow

Env.

Python,
Tensorflow

–

–

2007–2014

Text, sentence

Sentence vector +
DFFN

Usefulness,
F1-score, AUROC

2007–2014

–

–

2008–2014

Financial ratios
and news text

Car, insurance and
accident related
features

Transaction data

Insured’s id,
area-code, gender,
etc.

Sentences,
StockTwits
messages

doc2vec + NN

Relative usefulness

Doc2vec

DMLP + LDA

TP, FP, Accuracy,
Precision, F1-score

LSTM

RNN

Doc2vec, CNN

t-SNE

Accuracy, total
error

Accuracy,
precision, recall,
f-measure, AUC

–

–

Python

Python,
Tensorflow

[196]

StockTwits

2015–2016

word vectors for RNN-RBM-DBN network was proposed to pre-

et al. [182] proposed a method that used word embeddings with

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

28

dict the stock prices. Buczkowski et al. [180] proposed a novel

word2Vec, technical analysis features and stock prices for price

method that used expert recommendations, ensemble of GRU and

prediction. In [183], Deep Neural Generative Model (DGM) with

LSTM for prediction of the prices.

news articles using Paragraph Vector algorithm was used for cre-

In [181] a novel method that used character-based neural

ation of the input vector to predict the stock prices. In [184], the

language model using financial news and LSTM was proposed. Liu

stock price data and word embeddings were used for stock price

[194]

Art.

[72]

[86]

[87]

[88]

[121]

[123]

[195]

News from NowNews,
AppleDaily, LTN,
MoneyDJ for 18 stocks

The event data set for
large European banks,
news articles from
Reuters

Event dataset on
European banks, news
from Reuters

News from Reuters,
fundamental data

Real-world data for
automobile insurance
company labeled as
fradulent

Financial transactions

Taiwan’s National
Pension Insurance

Deep learning for financial applications:
Other theoretical or conceptual studies

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

19

Table 14
Other - theoretical or conceptual studies.

Art.

[197]

[198]

SubTopic

Analysis of AE, SVD

Fraud Detection in
Banking

IsTimeSeries?

Data set

Yes

No

Selected stocks from the
IBB index and stock of
Amgen Inc.

Risk Management /
Fraud Detection

Period

2012–2014

Feature set

Price data

Method

AE, SVD

–

–

DRL

prediction. The results showed that the extracted information
from embedding news improves the performance.

Rawte et al. [85] tried to solve three separate problems using
CNN, LSTM, SVM, RF: Bank risk classification, sentiment analy-
sis and Return on Assets (ROA) regression. Akhtar et al. [185]
compared CNN, LSTM and GRU based DL models against MLP
for financial sentiment analysis. Chang et al. [186] implemented
the estimation of information content polarity (negative/positive
effect) with text mining, word vector, lexical, contextual input
and various LSTM models. They used the financial news from
Reuters.

Jangid et al. [187] proposed a novel method that is a com-
bination of LSTM and CNN for word embedding and sentiment
analysis using Bidirectional LSTM (Bi-LSTM) for aspect extraction.
The proposed method used multichannel CNN for financial sen-

4.9. Theoretical or conceptual studies

There were a number of research papers that were either
focused on the theoretical concepts of finance or the conceptual
designs without model implementation phases; however they
still provided valuable information, so we decided to include
them in our survey. In Table 14, these studies were tabulated
according to their topic of interest.

In [197], the connection between deep AEs and Singular Value
Decomposition (SVD) were discussed and compared using stocks
from iShares Nasdaq Biotechnology ETF (IBB) index and the stock
of Amgen Inc. Bouchti et al. [198] explained the details of DRL
and mentioned that DRL could be used for fraud detection/risk
management in banking.

29

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

timent analysis. Shijia et al. [188] used an attention-based LSTM

for the financial sentiment analysis using news headlines and mi-

croblog messages. Sohangir et al. [189] used LSTM, doc2vec, CNN

and stock market opinions posted in StockTwits for sentiment

analysis. Mahmoudi et al. [190] extracted tweets from StockTwits

to identify the user sentiment. In the evaluation approach, they

also used emojis for the sentiment analysis. Kitamori et al. [191]

extracted the sentiments from financial news and used DMLP to

classify positive and negative news.

In [192], the sentiment/aspect prediction was implemented

using an ensemble of LSTM, CNN and GRU networks. In a different

study, Li et al. [193] proposed a DL based sentiment analysis

method using RNN to identify the top sellers in the underground

4.10. Other financial applications

Finally, there were some research papers which did not fit into

any of the previously covered topics. Their data set and intended

output were different than most of the other studies focused

in this survey. These studies include social security payment

classification, bank telemarketing success prediction, hardware

solutions for faster financial transaction processing, etc. There

were some anomaly detection implementations like tax evasion,

money laundering that could have been included in this group;

however we decided to cover them in a different subsection,

fraud detection. Table 15 shows all these aforementioned studies

economy. Moore et al. [194] used text mining techniques for

with their differences.

sentiment analysis from the financial news.

Dixon et al. [199] used Intel Xeon Phi to speedup the price

In [195], individual social security payment types (paid, un-

movement direction prediction problem using DFFN. The main

paid, repaid, transferred) were classified and predicted using

contribution of the study was the increase in the speed of pro-

LSTM, HMM and SVM. Sohangir et al. [196] used two neural

network models (doc2Vec, CNN) to find the top authors in Stock-

Twits messages and to classify the authors as expert or non-

expert for author classification purposes.

In [123], the character sequences in financial transactions and

the responses from the other side was used to detect if the

transaction was fraud or not with LSTM. Wang et al. [121] used

text mining and DMLP models to detect automobile insurance

In [86], the news semantics were extracted by the word se-

quence learning, bank stress was determined and classified with

the associated events. Day et al. [72] used financial sentiment

analysis using text mining and DMLP for stock algorithmic trad-

fraud.

ing.

Cerchiello et al. [88] used the fundamental data and text

mining from the financial news (Reuters) to classify the bank

distress. In [87], the bank distress was identified by extracting the

data from the financial news through text mining. The proposed

method used DFNN on semantic sentence vectors to classify if

there was an event or not.

cessing. Alberg et al. [200] used several company financials data

(fundamental data) and price together to predict the next period’s

company financials data. Kim et al. [201] used CNN for predicting

the success of bank telemarketing. In their study, they used the

phone calls of the bank marketing data and 16 finance-related

attributes. Lee et al. [202] used technical indicators and patent

information to estimate the revenue and profit for the corporates

using RBM based DBN, FFNN and Support Vector Regressor (SVR).

Ying et al. [195] classified and predicted individual social

security payment types (paid, unpaid, repaid, transferred) using

LSTM, HMM and SVM. Li et al. [193] proposed a deep learning-

based sentiment analysis method to identify the top sellers in

the underground economy. Jeong et al. [47] combined deep Q-

learning and deep NN to implement a model to solve three

separate problems: Increasing profit in a market, prediction of

the number of shares to trade, and preventing overfitting with

insufficient financial data.

5. Current snaphot of DL research for financial applications

4.8.1. Model, feature and dataset selections for financial text mining

Financial text mining is highly correlated with financial senti-

ment analysis. So, most of the highlights described for financial

sentiment analysis are also valid for financial text mining. Full

For the survey, we reviewed 144 papers from various financial

application areas. Each paper is analyzed according to its topic,

publication type, problem type, method, dataset, feature set and

performance criteria. Due to space limitations, we will only pro-

distribution of models, features and datasets used by the financial

vide the general summary statistics indicating the current state

text mining implementations are presented in Figs. 10–12.

of the DL for finance research.

20

Table 15
Other financial applications.

Deep learning for financial applications:
Other financial applications

A.M. Ozbayoglu, M.U. Gudelek and O.B. Sezer / Applied Soft Computing Journal 93 (2020) 106384

Art.

[47]

[193]

Subtopic

Data set

Period

Feature set

Method

Performance criteria

Env.

Improving trading
decisions

S&P500, KOSPI, HSI,
and EuroStoxx50

1987–2017

200-days stock price

Deep Q-Learning and
DMLP

Total profit,
Correlation

Identifying Top
Sellers In
Underground
Economy

Forums data

2004–2013

Sentences and
keywords

Recursive neural
tensor networks

Precision, recall,
f-measure

–

–

[195]

Predicting Social Ins.
Payment Behavior

Taiwan’s National
Pension Insurance

2008–2014

Insured’s id,
area-code, gender,
etc.

Accuracy, total error

Python

1991–2014

Price data

–

RNN

DNN

[199]

Speedup

[200]

Forecasting
Fundamentals

[201]

[202]

Predicting Bank
Telemarketing

Corporate
Performance
Prediction

45 CME listed
commodity and FX
futures

Stocks in NYSE,
NASDAQ or AMEX
exchanges

Phone calls of bank
marketing data

22 pharmaceutical
companies data in US
stock market

1970–2017

2008–2010

2000–2015

16 fundamental
features from balance
sheet

16 finance-related
attributes

11 financial and 4
patent indicator

DMLP, LFM

MSE, Compound
annual return, SR

CNN

Accuracy

RBM, DBN

RMSE, profit

–

–

–

–

Source: Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications: A survey." Applied Soft
Computing (2020): 106384.

30

Fig. 8. The histogram of publication count in topics.

First and foremost, we clustered the various topics within the

application areas. However, since it is a natural extension of its

financial applications research and presented them in Fig. 8. A

shallow counterpart MLP, it has a longer history than the other

quick glance at the figure shows us financial text mining and

DL models.

algorithmic trading are the top two fields that the researchers

CNN started getting more attention lately since most of the

most worked on followed by risk assessment, sentiment analysis,

implementations appeared within the past 3 years. Careful anal-

portfolio management and fraud detection, respectively. The re-

ysis of CNN papers indicates that a recent trend of representing

sults indicate most of the papers were published within the past

financial data with a 2-D image view in order to utilize CNN

3 years implying the domain is very hot and actively studied.

is growing. Hence CNN based models might overpass the other

When the papers were clustered by the DL model type as

models in the future. It actually passed DMLP for the past 3 years.

presented in Fig. 9, we observe the dominance of RNN, DMLP

Furthermore, we attempted to provide more details about

and CNN over the remaining models, which might be expected,

associations between the DL models and the financial application

since these models are the most commonly preferred ones in

areas. Fig. 10 gives the distribution of the models for the research

general DL implementations. Meanwhile, RNN is a general um-

areas through a model-topic heatmap. Since most of the papers

brella model which has several versions including LSTM, GRU, etc.

had multiple DL models, the amount of models is more than

Within the RNN choice, most of the models actually belonged

the number of covered papers. The results indicate the broad

to LSTM, which is very popular in time series forecasting or

acceptance of RNN, DMLP and CNN models in almost all financial

regression problems. It is also used quite often in algorithmic

application areas.

trading. More than 70% of the RNN papers consisted of LSTM

We also wanted to elaborate on the particular feature se-

models.

lections for each financial application area to see if we could

Meanwhile, DMLP generally fits well for classification prob-

spot any pattern. Fig. 11 gives the distribution of the features

lems; hence it is a common choice for most of the financial

for the research areas through a feature-topic heatmap. Unlike

Financial time series forecasting with deep
learning: Topic-model heatmap

O.B. Sezer, M.U. Gudelek and A.M. Ozbayoglu / Applied Soft Computing Journal 90 (2020) 106181

21

Fig. 8. The histogram of publication count in years.

Source: Omer Berat Sezer, Mehmet Ugur Gudelek, and Ahmet Murat Ozbayoglu (2020), "Financial time series forecasting with deep learning:
A systematic literature review: 2005–2019." Applied Soft Computing 90 (2020): 106181.

Fig. 7. Topic-model heatmap.

though financial time series forecasting is a subset of time-series
studies, due to the embedded profit-making expectations from
successful prediction models, some differences exist, such that
higher prediction accuracy sometimes might not reflect a prof-
itable model. Hence, the risk and reward structure must also be
taken into consideration. At this point, we will try to elaborate on
our observations about these differences in various model designs
and implementations.

31

In addition to DMLP, CNN is also a popular choice for

classification-type financial time series forecasting implementa-

tions. Most of these studies appeared within the last 3 years. As

mentioned before, to convert time-varying sequential data into a

more stationary classifiable form, some preprocessing might be

necessary. Even though some 1-D representations exist, the 2-

D implementation for CNN is more common, mostly inherited

through image recognition applications of CNN from computer

vision implementations. In some studies [188,189,193,199,219],

innovative transformations of financial time series data into an

image-like representation have been adapted, and impressive

performances have been achieved. As a result, CNN might in-

crease its share of interest for financial time series forecasting

in the next few years.

As one final note, Fig. 13 shows which frameworks and plat-

forms the researchers and developers used while implementing

6.1. DL models for financial time series forecasting

According to the publication statistics, LSTM was the preferred

choice of most researchers for financial time series forecasting.

LSTM and its variations utilized time-varying data with feedback

embedded representations, resulting in higher performances for

time series prediction implementations. Because most financial

data, one way or another, included time-dependent components,

LSTM was the natural choice in financial time series forecasting

problems. Meanwhile, LSTM is a special DL model derived from a

more general classifier family, namely RNN.

Careful analysis of Fig. 11 illustrates the dominance of RNNs

(which mainly consist of LSTM). As a matter of fact, more than

half of the published papers on time series forecasting fall into

the RNN model category. Regardless of its problem type, price,

or trend prediction, the ordinal nature of the data represen-

their work. We tried our best to extract this information from the

tation forced researchers to consider RNN, GRU, and LSTM as

papers. However, we must keep in mind that not every publica-

viable preferences for their model choices. Hence, RNN models

tion provided their development environment. Also, most papers

were chosen, at least for benchmarking, in many studies for

did not give details, preventing us from a more thorough compar-

performance comparison with other developed models.

ison chart, i.e, some researchers claimed they used Python, but

Meanwhile, other models were also used for time series fore-

no further information was given, while some others mentioned

casting problems. Among those, DMLP had the most interest due

the use of Keras or TensorFlow, providing more details. Also,

to the market dominance of its shallow cousin (MLP) and its wide

within the ‘‘Other’’ section, the usage of Pytorch has increased

acceptance and long history within ML society. However, there is

in the last year or so, even though it is not visible from the

a fundamental difference in how DMLP- and RNN-based models

chart. Regardless, Python-related tools were the most influential

were used for financial time series prediction problems.

technologies behind the implementations covered in this survey.

DMLP fits well for both regression and classification problems.

6. Discussion and open issues

However, in general, data order independence must be preserved

to better utilize the internal working dynamics of such networks,

even though some adjustments can be made through the learning

From an application perspective, even though financial time

algorithm configuration. In most cases, either trend components

series forecasting has a relatively narrow focus, i.e., the imple-

of the data need to be removed from the underlying time series or

mentations were mainly based on price or trend prediction, de-

some data transformations might be needed so that the resulting

pending on the underlying DL model, very different and versatile

data becomes stationary. Regardless, some careful preprocessing

models exist in the literature. We must remember that even

might be necessary for a DMLP model to be successful. In contrast,

Stock price forecasting using only
raw time series data

O.B. Sezer, M.U. Gudelek and A.M. Ozbayoglu / Applied Soft Computing Journal 90 (2020) 106181

Table 1
Stock price forecasting using only raw time series data.

9

Data set

Period

Feature set

Lag

Horizon

Method

Performance criteria

Env.

38 stocks in KOSPI

2010–2014

1990–2015

Lagged stock
returns
OCHLV

50 min

5 min

DNN

30 d

3 d

LSTM

NMSE, RMSE, MAE,
MI
Accuracy

–

Theano, Keras

Art.

[80]

[81]

[82]

[83]

[84]

[85]

[86]

[87]

[88]

[89]

[90]

[91]

[92]

[93]

[94]

[95]

China stock
market, 3049
Stocks
Daily returns of
‘BRD’ stock in
Romanian Market
297 listed
companies of CSE
5 stock in NSE

Stocks of Infosys,
TCS and CIPLA
from NSE
10 stocks in
S&P500
Stocks data from
S&P500
High-frequency
transaction data of
the CSI300 futures
Stocks in the
S&P500
ACI Worldwide,
Staples, and
Seagate in
NASDAQ
Chinese Stocks

20 stocks in
S&P500
S&P500

12 stocks from SSE
Composite Index
50 stocks from
NYSE

2001–2016

OCHLV

–

1 d

LSTM

RMSE, MAE

Python, Theano

2012–2013

OCHLV

2 d

1 d

LSTM, SRNN, GRU

MAD, MAPE

Keras

1997–2016

2014

OCHLV, Price data,
turnover and
number of trades.
Price data

200 d

1..10 d

LSTM, RNN, CNN,
MLP

MAPE

–

–

RNN, LSTM and
CNN

Accuracy

–

–

1997–2016

OCHLV, Price data

36 m

1 m

RNN, LSTM, GRU

2011–2016

OCHLV

2017

Price data

1 d

–

1 d

DBN

1 min

DNN, ELM, RBF

Accuracy, Monthly
return
MSE, norm-RMSE,
MAE
RMSE, MAPE,
Accuracy

Keras,
Tensorflow
–

Matlab

1990–2015

Price data

2006–2010

Daily closing
prices

240 d

17 d

1 d

1 d

DNN, GBT, RF

RNN, ANN

Mean return, MDD,
Calmar ratio
RMSE

H2O

–

2007–2017

OCHLV

30 d

1..5 d

2010–2015

Price data

1985–2006

2000–2017

Monthly and daily
log-returns
OCHLV

–

*

–

1 d

60 d

1..7 d

DWNN

2007–2016

Price data

–

1d, 3 d,
5 d

SFM

CNN

+

LSTM

AE

+

LSTM

DBN

MLP

+

Annualized Return,
Mxm Retracement
Weekly Returns

Python

–

Validation, Test Error

MSE

MSE

Theano, Python,
Matlab
Tensorflow

–

32

Source: Omer Berat Sezer, Mehmet Ugur Gudelek, and Ahmet Murat Ozbayoglu (2020), "Financial time series forecasting with deep learning:
A systematic literature review: 2005–2019." Applied Soft Computing 90 (2020): 106181.

In another group of studies, some researchers again focused
on LSTM-based models. However, their input parameters came

with different classifiers. Ozbayoglu [104] used technical indica-
tors along with stock data on a Jordan–Elman network for price

from various sources including raw price data, technical and/or

prediction.

fundamental analysis, macroeconomic data, financial statements,

There were also multiple and hybrid models that used mostly

news, and investor sentiment. Table 2 summarizes these stock

technical analysis features as their inputs to the DL model. Several

price forecasting papers. In Table 2, different methods/models

technical indicators were fed into LSTM and MLP networks in

are also listed based on five sub-groups: DNN model; LSTM and

Khare et al. [105] for intraday price prediction. Recently, Zhou

RNN models; multiple and hybrid models; CNN model; and novel

et al. [106] used a GAN for minimizing Forecast error loss and Di-

methods.

rection prediction loss (GAN-FD) model for stock price prediction

DNN models were used in some stock price forecasting pa-

and compared their model performances against ARIMA, ANN and

pers within this group. In Abe et al. [96], a DNN model and 25

Support Vector Machine (SVM). Singh et al. [107] used several

fundamental features were used for prediction of Japan Index

technical indicator features and time series data with Principal

constituents. Feng et al. [97] also used fundamental features and

Component Analysis (PCA) for dimensionality reduction cascaded

a DNN model for prediction. A DNN model and macro economic

with a DNN (2-layer FFNN) for stock price prediction. Karaoglu

data, such as GDP, unemployment rate, and inventories, were

et al. [108] used market microstructure-based trade indicators

used by the authors of [98] for the prediction of U.S. low-level

as inputs into an RNN with Graves LSTM detecting the buy–

disaggregated macroeconomic time series.

sell pressure of movements in the Istanbul Stock Exchange Index

LSTM and RNN models were chosen in some studies. Kraus and

(BIST) to perform price prediction for intelligent stock trading. In

Feuerriegel [99] implemented LSTM with transfer learning using

Zhou et al. [109], next month’s return was predicted, and next-to-

text mining through financial news and stock market data. Sim-

be-performed portfolios were constructed. Good monthly returns

ilarly, Minami et al. [100] used LSTM to predict stock’s next day

were achieved with LSTM and LSTM-MLP models.

price using corporate action events and macro-economic index.

Meanwhile,

in some papers, CNN models were preferred.

Zhang and Tan [101] implemented DeepStockRanker, an LSTM-

Abroyan et al. [110] used 250 features, including order details,

based model for stock ranking using 11 technical indicators. In

for the prediction of a private brokerage company’s real data of

Zhuge et al. [102], the authors used the price time series and

risky transactions. They used CNN and LSTM for stock price fore-

emotional data from text posts to predict the opening stock price

casting. The authors of [111] used a CNN model and fundamental,

of the next day with an LSTM network. Akita et al. [103] used

technical, and market data for prediction.

textual information and stock prices through Paragraph Vector +

Novel methods were also developed in some studies. In Tran

LSTM for forecasting prices and the comparisons were provided

et al. [112], with the FI-2010 dataset, bid/ask and volume were

10

Stock price forecasting using various data

O.B. Sezer, M.U. Gudelek and A.M. Ozbayoglu / Applied Soft Computing Journal 90 (2020) 106181

Table 2
Stock price forecasting using various data.

Art.

[96]

[97]

[98]

[99]

[100]

[101]

[102]

[103]

[104]

[105]

[106]

[107]

[108]

[109]

[110]

[111]

[112]

[113]

Data set

Japan Index
constituents from
WorldScope
Return of S&P500

U.S. low-level
disaggregated
macroeconomic
time series
CDAX stock
market data

Stock of Tsugami
Corporation
Stocks in China’s
A-share
SCI prices

10 stocks in
Nikkei 225 and
news
TKC stock in NYSE
and QQQQ ETF
10 Stocks in NYSE

42 stocks in
China’s SSE
Google’s daily
stock data
GarantiBank in
BIST, Turkey
Stocks in NYSE,
AMEX, NASDAQ,
TAQ intraday trade
Private brokerage
company’s real
data of risky
transactions
Fundamental and
Technical Data,
Economic Data

The LOB of 5
stocks of Finnish
Stock Market
Returns in NYSE,
AMEX, NASDAQ

Period

1990–2016

1926–2016

1959–2008

2010–2013

Feature set

25 Fundamental
Features

Fundamental
Features:
GDP,
Unemployment
rate, Inventories,
etc.
Financial news,
stock market data

2013

Price data

2006–2007

2008–2015

2001–2008

1999–2006

–

2016

2004–2015

2016

1993–2017

–

–

2010

1975–2017

11 technical
indicators
OCHL of change
rate, price
Textual
information and
Stock prices
Technical
indicators, Price
Price data,
Technical
indicators
OCHLV, Technical
Indicators
OCHLV, Technical
indicators
OCHLV, Volatility,
etc.
Price, 15 firm
characteristics

250 features:
order details, etc.

Fundamental ,
technical and
market
information
FI-2010 dataset:
bid/ask and
volume
57 firm
characteristics

Lag

10 d

–

–

Horizon

Method

Performance criteria

Env.

1 d

DNN

1 s

–

DNN

DNN

Correlation, Accuracy,
MSE

Tensorflow

MSPE

R2

Tensorflow

–

20 d

1 d

LSTM

242 min

1 min

GAN (LSTM, CNN)

–

–

7 d

10 d

–

1 d

–

–

50 d

1 d

20 min

1 min

20 d

–

80 d

–

–

–

*

1 d

–

1 d

–

–

*

–

MSE, RMSE, MAE,
Accuracy, AUC

RMSE

AR, IR, IC

TensorFlow,
Theano, Python,
Scikit-Learn
Keras,
Tensorflow
–

LSTM

LSTM

EmotionalAnalysis

MSE

LSTM

+
Paragraph Vector

Profit

–

–

LSTM

+

RNN
(Jordan–Elman)
LSTM, MLP

(2D)2 PCA

DNN

+

PLR, Graves LSTM

LSTM

MLP

+

Profit, MSE

Java

RMSE

RMSRE, DPA, GAN-F,
GAN-D
SMAPE, PCD, MAPE,
RMSE, HR, TR, R2
MSE, RMSE, MAE,
RSE, R2
Monthly return, SR

CNN, LSTM

F1-Score

CNN

–

WMTR, MDA

Accuracy, Precision,
Recall, F1-Score

–

–

R, Matlab

Spark

Python,Keras,
Tensorflow in
AWS
Keras,
Tensorflow

–

–

Fama–French
n-factor model DL

R2, RMSE

Tensorflow

Source: Omer Berat Sezer, Mehmet Ugur Gudelek, and Ahmet Murat Ozbayoglu (2020), "Financial time series forecasting with deep learning:
stochastic oscillator to create inputs for a Recurrent CNN (RCNN)
A systematic literature review: 2005–2019." Applied Soft Computing 90 (2020): 106181.
for stock price prediction. Iwasaki et al. [117] also used sentiment

used as the feature set for forecasting. In the study, they pro-
posed Weighted Multichannel Time-series Regression (WMTR),

and Multilinear Discriminant Analysis (MDA). Feng et al. [113]

analyses through text mining and word embeddings from analyst

used 57 characteristic features, including Market equity, Mar-

reports and used sentiment features as inputs to a DFNN model

ket Beta, Industry momentum, and Asset growth, as inputs to

for stock price prediction. Then, different portfolio selections

a Fama–French n-factor DL for predicting monthly US equity

were implemented based on the projected stock returns.

returns in New York Stock Exchange (NYSE), American Stock

GRU, LSTM, and RNN models were preferred in the next group

Exchange (AMEX), or NASDAQ.

of papers. Das et al. [118] implemented sentiment analysis on

A number of research papers have also used text mining tech-

Twitter posts along with stock data for price forecasting using an

niques for feature extraction but used non-LSTM models for stock

RNN. Similarly, the authors of [119] used sentiment classification

price prediction. Table 3 summarizes the stock price forecasting

(neutral, positive, and negative) for opening or closing stock

papers that used text mining techniques. In Table 3, different

price prediction with various LSTM models. They compared their

methods/models are clustered into three sub-groups: CNN and

results with SVM and achieved higher overall performance. In

LSTM models; GRU, LSTM, and RNN models; and novel methods.

Zhongshengz et al. [120], text and price data were used for the

CNN and LSTM models were adapted in some of the papers.

prediction of SSE Composite Index (SCI) prices.

In Ding et al. [114], events were detected from Reuters and

Novel approaches were reported in some papers. Nascimento

Bloomberg news through text mining, and that information was

et al. [121] used word embeddings for extracting information

used for price prediction and stock trading through the CNN

from web pages and then combined it with stock price data

model. Vargas et al. [115] used text mining on S&P500 index

for stock price prediction. They compared the Autoregressive

news from Reuters through an LSTM

CNN hybrid model for

(AR) model and RF with and without news. The results showed

price prediction and intraday directional movement estimation

embedding news information improved the performance. Han

+

together. Lee et al. [116] used financial news data and imple-

et al. [122] used financial news and the ACE2005 Chinese cor-

mented word embedding with Word2vec along with MA and

pus. Different event types of Chinese companies were classified

33

O. Bustos and A. Pomares-Quimbaya / Expert Systems With Applications 156 (2020) 113464

5

Stock Market Movement Forecast:
Phases of the stock market modeling
Fig. 2. Count of articles by publication year.

Source: O. Bustos and A. Pomares-Quimbaya (2020), "Stock Market Movement Forecast: A Systematic Review."
Expert Systems with Applications (2020): 113464.

Fig. 3. Phases of the stock market modeling .

34

the time series of historical stock prices, which can be used di-

rectly by different computational models.

3.1.1. Stock values

Given the technical analysis approach, stock prices reﬂect all the

information required to understand market behavior. In this way,

the important thing is to analyze the series of time correspond-

ing to the prices. Generally, this information is public and free and

can be downloaded from the pages of the stock markets (such as

Nasdaq Kazem, Shariﬁ, Hussain, Saberi, & Hussain (2013) ), third

parties (such as Yahoo Finance Wen, Yang, Song, & Jia (2010) ). Be-

sides, some companies like Bloomberg ( Ding, Zhang, Liu, & Duan,

2015 ) provide paid services with more information related to stock

prices.

In some articles, daily stock information is used, which consists

of the opening price (OP), closing price (CP), the maximum (MAX)

and minimum price (MIN), and the volume (VOL) of transactions

performed Wang, Liu, Shang, and Wang (2018) Fischer and Krauss

(2018) Di Persio and Honchar (2016) . Closing prices are the most

commonly used information, but the volume and ranges have also

shown value in the prediction. Most of the studies employ a time-

span of 10 0 0 days, that can be handled easily for most of the ma-

chine learning algorithms.

In addition, there are other studies that use intraday informa-

tion for prediction ( Huang & Li, 2017; Tsantekidis et al., 2017 ). The

most ﬁne-grained intraday information is the bid-ask price for a

stock. When a stock is being traded in an exchange, there are buy-

ers and sellers interested in trading that stock. Ask price is the

minimum price a seller is willing to accept, while the bid price

is the maximum price that the buyer offers to pay for the share.

The consolidation of all these prices leads to an enormous number

Fig. 4. Classiﬁcations of inputs.

reviewed use structured type inputs, for which processing tech-

niques already exist, and their importance has been extensively

studied. Most recent ones allow the use of unstructured informa-

tion, which is more diﬃcult to process and to extract useful infor-

mation. Fig. 4 shows a proposed taxonomy for the inputs used to

forecast the stock market in the analyzed studies.

3.1. Structured inputs

The structured information refers to data groups with a prede-

of points having to be recorded to predict the intraday price.

ﬁned skeleton, organized in tabular form, where the characteristics

or attributes can be described as columns of a table. That struc-

3.1.2. Technical indicators

ture makes information more accessible to navigate, and simple or

Technical indicators have been useful for predicting the stock

complex searches can be done without further effort. Most arti-

market. These have been increasing in sophistication, and are al-

cles use this type of information, which is usually open and ex-

ready  part  of  the  language  of  brokers.  Technical  indicators  can

posed through API programming interfaces. The most common is

summarize the behavior or trends in the time series, making their

Algorithmic
Trading

35

Algorithmic Trading

Historical
Finance Market
Data

Live Finance
Market Data

Computer
Program

Order Status

Order

Broker API

Backtest
Results

Order

Order Status

Broker’s
Server

Source: Ernest P. Chan (2017), Machine Trading: Deploying Computer Algorithms to Conquer the Markets, Wiley

36

Risk and Return

Source: Bacon, Carl. "How sharp is the Sharpe-ratio?-Risk-adjusted Performance Measures." Statpro White Paper (2000).

37

Sharpe Ratio

𝐒𝐡𝐚𝐫𝐩𝐞 𝐑𝐚𝐭𝐢𝐨

=

𝑃𝑜𝑟𝑡𝑜𝑓𝑜𝑙𝑖𝑜 𝑅𝑒𝑡𝑢𝑟𝑛 − 𝑅𝑖𝑠𝑘 𝐹𝑟𝑒𝑒 𝑅𝑒𝑡𝑢𝑟𝑛
𝑃𝑜𝑟𝑡𝑜𝑓𝑜𝑙𝑖𝑜 𝑅𝑖𝑠𝑘

Source: Bacon, Carl. "How sharp is the Sharpe-ratio?-Risk-adjusted Performance Measures." Statpro White Paper (2000).

38

Sharpe Ratio

𝐒𝐡𝐚𝐫𝐩𝐞 𝐑𝐚𝐭𝐢𝐨 𝑆𝑅 =

𝑟! − 𝑟"
𝜎!

Where
rP = portfolio return
rF = risk free rate
σP = portfolio risk (variability, standard deviation of return)

Source: Bacon, Carl. "How sharp is the Sharpe-ratio?-Risk-adjusted Performance Measures." Statpro White Paper (2000).

39

Sortino Ratio

𝑟! − 𝑟#
𝜎$

𝐒𝐨𝐫𝐭𝐢𝐧𝐨 𝐑𝐚𝐭𝐢𝐨 =

Where
rP = portfolio return
rT = Minimum Target Return
σD = Downside Risk

%
𝐃𝐨𝐰𝐧𝐬𝐢𝐝𝐞 𝐑𝐢𝐬𝐤 𝜎! = -
"#$

min 𝑟𝑖 − 𝑟𝑇 , 0 2
𝑛

Source: Bacon, Carl. "How sharp is the Sharpe-ratio?-Risk-adjusted Performance Measures." Statpro White Paper (2000).

40

Max Drawdown

Source: Bacon, Carl. "How sharp is the Sharpe-ratio?-Risk-adjusted Performance Measures." Statpro White Paper (2000).

41

Portfolio Optimization
Efficient Frontier

Efficient Frontier

n
r
u
t
e
R

Risk

Source: Tucker Balch (2012), Investment Science: Portfolio Optimization,
https://www.youtube.com/watch?v=5qbMhXXq0vI

42

Backtesting

• Financial Functions (ffn)

• https://pmorissette.github.io/ffn/

• backtesting.py

• https://kernc.github.io/backtesting.py/

• Visualization

• Plotly Express (px)

• https://plotly.com/python/plotly-express/

• Bokeh

• https://bokeh.org/

43

Financial Functions (ffn)
plotly.express (px)

!pip install ffn
import ffn
import plotly.express as px
%pylab inline
#BTC-USD Bitcoin USD
df = ffn.get('btc-usd', start='2016-01-01', end='2021-12-31')
print('df')
print(df.head())
print(df.tail())
print(df.describe())
df.plot(figsize=(14,10))

returns = df.to_returns().dropna()
print('returns')
print(returns.head())
print(returns.tail())
print(returns.describe())
#ax = df.plot(figsize=(12,9))

perf = df.calc_stats()
perf.plot(figsize=(14, 10))
print(perf.display())

fig = px.line(df, x=df.index, y="btcusd", title='btcusd')
fig.update_layout(title='btcusd price', xaxis_title='Date', yaxis_title='Price')
#fig.update_traces(mode='markers+lines')
fig.show()

fig = px.line(returns, x=returns.index, y="btcusd", title='btcusd')
fig.update_layout(title='btcusd returns', xaxis_title='Date', yaxis_title='Returns')
fig.show()

fig = px.histogram(returns, x='btcusd', nbins=40, histnorm='probability', width=800, height=400)
fig.update_layout(title='btcusd returns histogram')
fig.show()

fig = px.box(returns, y='btcusd', points = 'all')
fig.update_layout(title='btcusd returns box')
fig.update_traces(boxmean='sd')
fig.show()

44

Financial Functions (ffn)
plotly.express (px)

# Upgrade pandas-datareader
!pip install --upgrade pandas
!pip install --upgrade pandas-datareader

!pip install ffn
import ffn
import plotly.express as px
%pylab inline
#BTC-USD Bitcoin USD
df = ffn.get('btc-usd', start='2016-01-01', end='2021-12-31')
print('df')
print(df.head())
print(df.tail())
print(df.describe())
df.plot(figsize=(14,10))

45

Financial Functions (ffn)
plotly.express (px)

returns = df.to_returns().dropna()
print('returns')
print(returns.head())
print(returns.tail())
print(returns.describe())
#ax = df.plot(figsize=(12,9))

46

Financial Functions (ffn)
plotly.express (px)

perf = df.calc_stats()
perf.plot(figsize=(14, 10))
print(perf.display())

fig = px.line(df, x=df.index, y="btcusd", title='btcusd')
fig.update_layout(title='btcusd price', xaxis_title='Date',
yaxis_title='Price')
#fig.update_traces(mode='markers+lines')
fig.show()

fig = px.line(returns, x=returns.index, y="btcusd", title='btcusd')
fig.update_layout(title='btcusd returns', xaxis_title='Date',
yaxis_title='Returns')
fig.show()

47

Financial Functions (ffn)
plotly.express (px)

fig = px.histogram(returns, x='btcusd', nbins=40,
histnorm='probability', width=800, height=400)

fig.update_layout(title='btcusd returns histogram')
fig.show()

fig = px.box(returns, y='btcusd', points = 'all')
fig.update_layout(title='btcusd returns box')
fig.update_traces(boxmean='sd')
fig.show()

48

Financial Functions (ffn)

btcusd

Date
2016-01-01  434.334015
2016-01-02  433.437988
2016-01-03  430.010986
2016-01-04  433.091003
2016-01-05  431.959991

btcusd
Date
2021-12-28  47588.855469
2021-12-29  46444.710938
2021-12-30  47178.125000
2021-12-31  46306.445312
2022-01-01  47686.812500

btcusd
count   2193.000000
mean   13025.164562
std    16489.530523
min      364.330994
25%     2589.409912
50%     7397.796875
75%    11358.662109
max    67566.828125

49

Financial Functions (ffn)
calc_stats() display()

Stat                 btcusd
------------------- ----------
Start                2016-01-01
End                  2022-01-01
Risk-free rate       0.00%

Total Return         10879.29%
Daily Sharpe         1.18
Daily Sortino
1.95
CAGR                 118.79%
Max Drawdown         -83.40%
Calmar Ratio         1.42

50

Financial Functions (ffn)
calc_stats() display()

MTD                  2.98%
3m                   -0.89%
6m                   42.04%
YTD                  2.98%
1Y                   62.34%
3Y (ann.)            131.46%
5Y (ann.)            116.71%
10Y (ann.)           -
Since Incep. (ann.)  118.79%

51

Financial Functions (ffn)
calc_stats() display()

Daily Sharpe         1.18
1.95
Daily Sortino
Daily Mean (ann.)    74.04%
Daily Vol (ann.)     62.94%
Daily Skew           -0.10
Daily Kurt           7.30
Best Day             25.25%
Worst Day            -37.17%

52

Financial Functions (ffn)
calc_stats() display()

Monthly Sharpe       1.38
Monthly Sortino
3.75
Monthly Mean (ann.)  114.20%
Monthly Vol (ann.)   82.59%
Monthly Skew         0.43
Monthly Kurt         -0.16
Best Month           69.63%
Worst Month          -36.41%

53

Financial Functions (ffn)
calc_stats() display()

Yearly Sharpe        0.54
9.73
Yearly Sortino
Yearly Mean          292.22%
Yearly Vol           542.38%
Yearly Skew          2.17
Yearly Kurt          4.86
Best Year            1368.90%
Worst Year           -73.56%

54

Financial Functions (ffn)
calc_stats() display()

Avg. Drawdown        -10.25%
Avg. Drawdown Days   36.55
Avg. Up Month        25.13%
Avg. Down Month      -12.35%
Win Year %           83.33%
Win 12m %            85.48%

55

Visualization
plotly.express (px)

56

Backtesting Output

backtesing output
Start                     2016-01-01 00:00:00
End                       2022-01-01 00:00:00
Duration                   2192 days 00:00:00
Exposure Time [%]                   97.993616
Equity Final [$]               4237449.058157
Equity Peak [$]                6165339.439633
Return [%]                        4137.449058
Buy & Hold Return [%]            10879.294935
Return (Ann.) [%]                   86.557668
Volatility (Ann.) [%]              144.748975
Sharpe Ratio                         0.597985
Sortino Ratio                        1.946086
Calmar Ratio                         1.362652
Max. Drawdown [%]                  -63.521467
Avg. Drawdown [%]                  -12.142095
Max. Drawdown Duration      557 days 00:00:00
Avg. Drawdown Duration       44 days 00:00:00
# Trades                                  116
Win Rate [%]                        35.344828
Best Trade [%]                     119.026467
Worst Trade [%]                    -23.393531
Avg. Trade [%]                       3.291328
Max. Trade Duration          74 days 00:00:00
Avg. Trade Duration          19 days 00:00:00
Profit Factor                        2.293983
Expectancy [%]                       5.036865
SQN                                  1.236071
_strategy                            SmaCross
_equity_curve
...
_trades                        Size  Entry..

57

describe()

High       Low      Open     Close        Volume  Adj Close

count   2193.00   2193.00   2193.00   2193.00  2.193000e+03    2193.00
mean   13363.00  12616.08  13005.79  13025.16  1.757591e+10   13025.16
std    16935.24  15960.65  16480.00  16489.53  2.085247e+10   16489.53
min      374.95    354.91    365.07    364.33  2.851400e+07     364.33
25%     2682.26   2510.48   2577.77   2589.41  1.182870e+09    2589.41
50%     7535.72   7233.40   7397.13   7397.80  9.175292e+09    7397.80
75%    11570.79  11018.13  11354.30  11358.66  2.886756e+10   11358.66
max    68789.62  66382.06  67549.73  67566.83  3.509679e+11   67566.83

58

# Upgrade pandas-datareader
!pip install --upgrade pandas

!pip install --upgrade pandas-datareader Backtesting

!pip install backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

import pandas as pd
import pandas_datareader.data as web
df = web.DataReader("BTC-USD", 'yahoo', '2016-01-01', '2021-12-31')
df.to_csv('BTC-USD.csv')
print(df.head().round(2))
print(df.tail().round(2))
print(df.describe().round(2))

class SmaCross(Strategy):

n1 = 5
n2 = 20

def init(self):

close = self.data.Close
self.sma1 = self.I(SMA, close, self.n1)
self.sma2 = self.I(SMA, close, self.n2)

def next(self):

if crossover(self.sma1, self.sma2):

self.buy()

elif crossover(self.sma2, self.sma1):

self.sell()

bt = Backtest(df, SmaCross, cash=100000, commission=.002, exclusive_orders=True)

output = bt.run()
print('backtesing output')
print(output)

bt.plot()

59

#!pip install backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.lib import plot_heatmaps
from backtesting.test import SMA

import pandas as pd
import pandas_datareader.data as web

Backtesting

from google.colab import files
import time
#BTC-USD ETH-USD
v_symbol = 'BTC-USD'
v_time_start = '2016-01-01'
v_time_end = '2021-12-31'
v_to_csv_filename = v_symbol + '_' + v_time_start + '_' + v_time_end + '.csv'
df = web.DataReader(v_symbol, 'yahoo', v_time_start, v_time_end)
df.to_csv(v_to_csv_filename)

print(df.head().round(2))
print(df.tail().round(2))
print(df.describe().round(2))
v_n1 = 5 #5 #20 #60 #120
v_n2 = 200 #20 #60 #120 #240

60

Backtesting

class SmaCross(Strategy):

n1 = v_n1 #5
n2 = v_n2 #60

def init(self):

close = self.data.Close
self.sma1 = self.I(SMA, close, self.n1)
self.sma2 = self.I(SMA, close, self.n2)

def next(self):

if crossover(self.sma1, self.sma2):

self.buy()

elif crossover(self.sma2, self.sma1):

self.sell()

bt = Backtest(df, SmaCross, cash=100000, commission=.002, exclusive_orders=True)

stats = bt.run()

61

filename = v_symbol + '_' + v_time_start + '_' + v_time_end + '_' + 'MA_' +
str(v_n1) + '_' + str(v_n2) + '.csv'
print('filename:', filename)
stats.to_csv(filename)

Backtesting

print('backtesing stats')
print(stats)
bt.plot()

print('filename:\t', filename)
print("stats._strategy:\t", stats._strategy)
print("# Trades:\t", stats['# Trades'])
print("stats['Equity Final [$]']:\t", round(stats['Equity Final [$]'], 4))
print("stats['Avg. Trade [%]']:\t", round(stats['Avg. Trade [%]'], 4))
print("Sharpe Ratio:\t", round(stats['Sharpe Ratio'], 4))

#download file
time.sleep(1) # time sleep 1 second
files.download(filename)
print('file downloaded:', filename)

62

Backtesting

print('*****bt.optimize*****')
stats, heatmap = bt.optimize(

n1 = range(5, 65, 5),
n2 = range(10, 205, 5),
constraint = lambda param: param.n1 <param.n2,
maximize = 'Avg. Trade [%]',
max_tries = 600,
random_state = 0,
return_heatmap = True)

#'Equity Final [$]' 'Avg. Trade [%]'

optimize_strategy = stats._strategy

63

Backtesting

optimize_filename = v_symbol + '_' + v_time_start + '_' + v_time_end + '_' +
'bt_optimize_strategy' + str(optimize_strategy) + '.csv'
print('optimize_filename:', optimize_filename)
print('backtesing optimize strategy stats')
print(stats)
stats.to_csv(optimize_filename)
plot_heatmaps(heatmap, agg='mean', plot_width = 1800)

print('backtesting optimize strategy heatmap')
print(heatmap)
print('backtesting optimize strategy heatmap Top 10')
print(heatmap.sort_values().iloc[-10:])
hm = heatmap.groupby(['n1', 'n2']).mean().unstack()
print('backtesting optimize strategy heatmap mean')
print(hm)
hm_filename = v_symbol + '_' + v_time_start + '_' + v_time_end + '_' +
'hm_heatmap.csv'
hm.to_csv(hm_filename)

64

Backtesting

print("filename:\t", optimize_filename)
print("stats._strategy:\t", stats._strategy)
print("# Trades:\t", stats['# Trades'])
print("stats['Equity Final [$]']:\t", round(stats['Equity Final [$]'], 4))
print("stats['Avg. Trade [%]']:\t", round(stats['Avg. Trade [%]'], 4))
print("Sharpe Ratio:\t", round(stats['Sharpe Ratio'], 4))

#download file
time.sleep(1) # time sleep 1 second
files.download(hm_filename)
print('file downloaded:', hm_filename)
files.download(optimize_filename)
print('file downloaded:', optimize_filename)

65

Backtesting

66

Time series data for EUR/USD and SMAs

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

67

Time series data for EUR/USD, SMAs, and
resulting positions

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

68

Gross performance of passive benchmark
investment and SMA strategy

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

69

Gross performance of the SMA strategy before
and after transaction costs

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

70

Gross performance of the passive benchmark
investment and the daily DNN strategy
(in-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

71

Gross performance of the passive benchmark
investment and the daily DNN strategy
(out-of-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

72

Gross performance of the daily DNN strategy
before and after transaction costs
(out-of-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

73

Gross performance of the passive benchmark
investment and the DNN intraday strategy
(out-of-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

74

Gross performance of the DNN intraday strategy
before and after higher/ lower transaction costs
(out-of-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

75

Gross performance on training and
validation data set

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

76

Gross performance of the passive benchmark
investment and the trading bot (out-of-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

77

Gross performance of the trading bot before and
after transaction costs (in-sample)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

78

Gross performance of the passive benchmark
investment and the trading bot
(vectorized and event-based backtesting)

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

79

Average true range (ATR) in absolute (price) and
relative (%) terms

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

80

BTC-USD

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

81

BTC-USD Returns

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

82

BTC-USD Returns Box

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

83

The Quant Finance PyData Stack

Source: http://nbviewer.jupyter.org/format/slides/github/quantopian/pyfolio/blob/master/pyfolio/examples/overview_slides.ipynb#/5

84

Yves Hilpisch (2020),
Artificial Intelligence in Finance:
A Python-Based Guide,
O’Reilly

Source: https://www.amazon.com/Artificial-Intelligence-Finance-Python-Based-Guide/dp/1492055433

85

Yves Hilpisch (2020),
Python for Algorithmic Trading:
From Idea to Cloud Deployment,
O’Reilly

Source: https://www.amazon.com/Python-Algorithmic-Trading-Cloud-Deployment/dp/149205335X

86

Stefan Jansen (2020),
Machine Learning for Algorithmic Trading:
Predictive models to extract signals from market and alternative data for systematic trading strategies
with Python, 2nd Edition,
Packt Publishing.

Source: https://www.amazon.com/Machine-Learning-Algorithmic-Trading-alternative/dp/1839217715/

87

Chris Kelliher (2022),
Quantitative Finance With Python:
A Practical Guide to Investment Management, Trading, and Financial Engineering,
Chapman and Hall/CRC.

Source: https://www.amazon.com/Quantitative-Finance-Python-Engineering-Mathematics/dp/1032014431/

88

Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly

https://github.com/yhilpisch/aiif

Source: https://github.com/yhilpisch/aiif

89

Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly

https://github.com/yhilpisch/aiif/tree/main/code

Source: https://github.com/yhilpisch/aiif/tree/main/code

90

Python in Google Colab (Python101)

https://colab.research.google.com/drive/1FEG6DnGvwfUbeo4zJ1zTunjMqf2RkCrT

https://tinyurl.com/aintpupython101

91

Python in Google Colab (Python101)

https://colab.research.google.com/drive/1FEG6DnGvwfUbeo4zJ1zTunjMqf2RkCrT

https://tinyurl.com/aintpupython101

92

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

93

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

94

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

95

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

96

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

97

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

98

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

99

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

100

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

101

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

102

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

103

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

104

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

105

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

106

Python in Google Colab (Python101)

https://tinyurl.com/aintpupython101

107

https://tinyurl.com/aintpupython101

108

Summary

• Algorithmic Trading
• Risk Management
• Trading Bot
• Event-Based Backtesting

Source: Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media.

109

References

• Yves Hilpisch (2020), Artificial Intelligence in Finance: A Python-Based Guide, O’Reilly Media,

https://github.com/yhilpisch/aiif .

• Yves Hilpisch (2020), Python for Algorithmic Trading: From Idea to Cloud Deployment, O’Reilly Media.
• Stefan Jansen (2020), Machine Learning for Algorithmic Trading: Predictive models to extract signals from market and

alternative data for systematic trading strategies with Python, 2nd Edition, Packt Publishing.

• Aurélien Géron (2019), Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow: Concepts, Tools, and

Techniques to Build Intelligent Systems, 2nd Edition, O’Reilly Media.

• Hariom Tatsat, Sahil Puri, Brad Lookabaugh (2020), Machine Learning and Data Science Blueprints for Finance: From

Building Trading Strategies to Robo-Advisors Using Python, O'Reilly Media

• Chris Kelliher (2022), Quantitative Finance With Python: A Practical Guide to Investment Management, Trading, and

Financial Engineering, Chapman and Hall/CRC.

• Abdullah Karasan (2021), Machine Learning for Financial Risk Management with Python: Algorithms for Modeling Risk,

O’Reilly Media.

• Ahmet Murat Ozbayoglu, Mehmet Ugur Gudelek, and Omer Berat Sezer (2020). "Deep learning for financial applications:

A survey." Applied Soft Computing (2020): 106384.

• Omer Berat Sezer, Mehmet Ugur Gudelek, and Ahmet Murat Ozbayoglu (2020), "Financial time series forecasting with

deep learning: A systematic literature review: 2005–2019." Applied Soft Computing 90 (2020): 106181.

• Min-Yuh Day (2022), Python 101, https://tinyurl.com/aintpupython101

110
