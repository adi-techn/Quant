import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ticker=["META","AMZN","NFLX","GOOG"]

stocks_data=yf.download(ticker,start="2025-01-01",end="2025-07-01")

stocks_data.to_csv("stocks_data.csv")

stocks=pd.read_csv("stocks_data.csv",header=[0,1],index_col=[0],parse_dates=[0])

stocks.columns=pd.MultiIndex.from_tuples(stocks.columns)
close=stocks.loc[:,"Close"].copy()

stock=stocks["Close"].copy()
ret=stock.pct_change().dropna()

#Another way to get mean & std
summary=ret.describe().T.loc[:,["mean","std"]]
summary["mean"]=summary["mean"]*126
summary["std"]=summary["std"]*np.sqrt(126)

summary.plot.scatter(x="std",y="mean",figsize=(6,4),s=50,fontsize=11)
for i in summary.index:
    plt.annotate(i,xy=(summary.loc[i,"std"]+0.002,summary.loc[i,"mean"]+0.002),size=13)
plt.xlabel("Annual Risk(std)",fontsize=15)
plt.ylabel("Annual Return( /100)",fontsize=15)
plt.title("Risk/Reward ",fontsize=15)
plt.show()

plt.figure(figsize=(8,6))
sns.set(font_scale=1.3)
sns.heatmap(ret.corr(),cmap="Reds",annot=True,annot_kws={"size":12},vmax=1)
plt.title("Correlation HeatMap")
plt.show()

plt.figure(figsize=(8,6))
sns.set(font_scale=1.3)
sns.heatmap(ret.cov(),cmap="Reds",annot=True,annot_kws={"size":12},vmax=0.001)
plt.title("Covariance HeatMap")
plt.show()
