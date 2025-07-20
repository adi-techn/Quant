import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st
import numpy as np
from stocknews import StockNews

st.set_page_config(layout='wide')
st.title("Stock Dashboard")
ticker=st.sidebar.text_input("Ticker")
start_date=st.sidebar.date_input('Start Date')
end_date=st.sidebar.date_input('End Date')

data=yf.download(ticker,start=start_date,end=end_date)
if data.empty:
    print("Increase Date Range")
else:
    fig=px.line(data,x=data.index,y=data['Close'].squeeze(),title=ticker)
st.plotly_chart(fig)

pricing_data,news=st.tabs(["Pricing Data","News"])

with pricing_data:
    st.header("Price Movement")
    d2=data
    d2['% Change']=data['Close']/data['Close'].shift(1)-1
    d2.dropna(inplace=True)
    st.write(d2)
    annual_ret=d2['% Change'].mean()*252*100
    st.write('Annual Return :',annual_ret,'%')

with news:
    st.header(f"News for {ticker}")
    sn=StockNews(ticker,save_news=False)
    df_news=sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        title_sentiment=df_news['sentiment_title'][i]
        st.write('Title Sentiment {title_sentiment}')
        news_sentiment=df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')
