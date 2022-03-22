from audioop import avg
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
import joblib
import pandas as pd
import json
import requests
import numpy as np
import random
from datetime import datetime
from pytz import timezone 
from django.views.decorators.csrf import csrf_exempt
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')
def home(request):
    
    return render(request,'accounts/dashboard.html')
# def calculate(request):
#     data = request.POST.get('company_name')
#     print(data)

#     # return HttpResponse("working")
#     return render(request,'accounts/dashboard.html')
def prediction(request):
    if(request.method == 'POST'):
        data_comp = request.POST.get('company_name')
        url = "https://alpha-vantage.p.rapidapi.com/query"

        querystring = {"symbol":str(data_comp),"function":"TIME_SERIES_INTRADAY","interval":"1min","output_size":"compact","datatype":"json"}

        headers = {
            'x-rapidapi-host': "alpha-vantage.p.rapidapi.com",
            'x-rapidapi-key': "f19d833b21msha1a10a46cd5a8b6p121be2jsnac0df7ca04d3"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response = json.loads(response.content.decode("UTF-8"))
        # df = pd.DataFrame(response)
        df1 = pd.DataFrame(response["Time Series (1min)"])
        df1 = df1.transpose()
        df1.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df1 = df1.iloc[::-1]
        df1 = df1.tail(1)
        df1.reset_index(inplace = True)
        df1.columns = ["Date", 'Open', 'High', 'Low', 'Close', 'Volume']
        df1['Volume'].replace(to_replace=0, method='ffill', inplace=True) 
        df1= df1.astype({ "Date": str, "Open": float, "High" : float, "Low" : float, "Close" : float, "Volume": int})
        first_column = df1.pop('Close')
        df1.insert(0, 'Close', first_column)

        url = "https://alpha-vantage.p.rapidapi.com/query"

        querystring = {"function":"TIME_SERIES_DAILY","symbol":str(data_comp),"outputsize":"compact","datatype":"json"}

        headers = {
            'x-rapidapi-host': "alpha-vantage.p.rapidapi.com",
            'x-rapidapi-key': "f19d833b21msha1a10a46cd5a8b6p121be2jsnac0df7ca04d3"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        response = json.loads(response.content.decode("UTF-8"))
        df = pd.DataFrame(response["Time Series (Daily)"])
        df = df.transpose()
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        curr_data = df.head(1)
        df = df.iloc[::-1]
        df = df.tail(1)
        df.reset_index(inplace = True)
        df.columns = ["Date", 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Volume'].replace(to_replace=0, method='ffill', inplace=True) 
        df= df.astype({ "Date": str, "Open": float, "High" : float, "Low" : float, "Close" : float, "Volume": int})
        first_column = df.pop('Close')
        df.insert(0, 'Close', first_column)
        l1 = list(calculate_change(df, df1))
        l1 = np.array(l1)
        # model = joblib.load("/home/ayush/Documents/stock_prediction/christopher/test_model")
        # print(model.predict(l1))
        # 
        pct_change = random.uniform(-1, 1)
        print("pct_change", pct_change)
        curr_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f')
        news_senti = calculate_news_prediction(request, str(data_comp))
        print("news_sentiment", news_senti)
        print(df["Open"])
        return render(request, "accounts/dashboard.html", {"comp" : data_comp, "open_price":df["Open"][0], "curr_price": curr_data["Open"][0], "pct_change":pct_change, "news_senti": news_senti, 'curr_time': curr_time})
    return render(request, "accounts/dashboard.html")

def calculate_change(df, dict1):
    return -(df["Open"][len(df)-1]-dict1["Open"])/df["Open"][len(df)-1], -(df["High"][len(df)-1]-dict1["High"])/df["High"][len(df)-1], -(df["Low"][len(df)-1]-dict1["Low"])/df["Low"][len(df)-1], -(df["Volume"][len(df)-1]-dict1["Volume"])/df["Volume"][len(df)-1]

@csrf_exempt
def calculate_news_prediction(request, data_company ):
# -*- coding: utf-8 -*-
    data_comp = data_company
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    finwiz_url = 'https://finviz.com/quote.ashx?t='

    import requests
    import pandas as pd
    url = "https://alpha-vantage.p.rapidapi.com/query"

    querystring = {"function":"TIME_SERIES_DAILY","symbol":data_comp,"outputsize":"7","datatype":"json"}

    headers = {
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com",
        'x-rapidapi-key': "f19d833b21msha1a10a46cd5a8b6p121be2jsnac0df7ca04d3"
        }
    import json
    response = requests.request("GET", url, headers=headers, params=querystring)
    response = json.loads(response.content.decode("UTF-8"))
    # df = pd.DataFrame(response)
    df = pd.DataFrame(response["Time Series (Daily)"])
    df_tr = df.transpose()

    tickers = [data_comp]
    news_tables={}
    for ticker in tickers:
        url = finwiz_url + ticker
        req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
        response = urlopen(req)    
        # Read the contents of the file into 'html'
        html = BeautifulSoup(response)
        # Find 'news-table' in the Soup and load it into 'news_table'
        news_table = html.find(id='news-table')
        # Add the table to our dictionary
        news_tables[ticker] = news_table

    # Read one single day of headlines for 'AMZN' 
    amzn = news_tables[data_comp]
    # Get all the table rows tagged in HTML with <tr> into 'amzn_tr'
    amzn_tr = amzn.findAll('tr')

    for i, table_row in enumerate(amzn_tr):
        # Read the text of the element 'a' into 'link_text'
        a_text = table_row.a.text
        # Read the text of the element 'td' into 'data_text'
        td_text = table_row.td.text
        # Print the contents of 'link_text' and 'data_text' 
        # print(a_text)
        # print(td_text)
        # Exit after printing 4 rows of data
        if i == 3:
            break

    parsed_news = []
    # Iterate through the news
    for file_name, news_table in news_tables.items():
        # Iterate through all tr tags in 'news_table'
        for x in news_table.findAll('tr'):
            # read the text from each tr tag into text
            # get text from a only
            text = x.a.get_text() 
            # splite text in the td tag into a list 
            date_scrape = x.td.text.split()
            # if the length of 'date_scrape' is 1, load 'time' as the only element

            if len(date_scrape) == 1:
                time = date_scrape[0]
                
            # else load 'date' as the 1st element and 'time' as the second    
            else:
                date = date_scrape[0]
                time = date_scrape[1]
            # Extract the ticker from the file name, get the string up to the 1st '_'  
            ticker = file_name.split('_')[0]
            
            # Append ticker, date, time and headline as a list to the 'parsed_news' list
            parsed_news.append([ticker, date, time, text])
            
    # parsed_news

    

    # Instantiate the sentiment intensity analyzer
    vader = SentimentIntensityAnalyzer()

    # Set column names
    columns = ['ticker', 'date', 'time', 'headline']

    # Convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
    parsed_and_scored_news = pd.DataFrame(parsed_news, columns=columns)

    # Iterate through the headlines and get the polarity scores using vader
    scores = parsed_and_scored_news['headline'].apply(vader.polarity_scores).tolist()

    # Convert the 'scores' list of dicts into a DataFrame
    scores_df = pd.DataFrame(scores)

    # Join the DataFrames of the news and the list of dicts
    parsed_and_scored_news = parsed_and_scored_news.join(scores_df, rsuffix='_right')

    import datetime
    # Convert the date column from string to datetime
    from datetime import date, timedelta 
    shipdatee = date.today()+ timedelta(days=-2)
    print(shipdatee)
    parsed_and_scored_news['date'] = pd.to_datetime(parsed_and_scored_news.date).dt.date
    # if(pd.to_datetime(parsed_and_scored_news.date).dt.date>=shipdatee):
    df1 = parsed_and_scored_news[pd.to_datetime(parsed_and_scored_news.date).dt.date>=shipdatee]
    print(df1.head())
    print(len(df1))
    return df1["compound"].mean()

