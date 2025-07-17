import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
from datetime import datetime, timedelta

# ---------- FUNCTIONS ----------

# Fetch stock data
def stock_data(ticker, period, interval):
    end_date = datetime.now()
    if period == '1wk':
        start_date = end_date - timedelta(days=7)
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    else:
        data = yf.download(ticker, period=period, interval=interval)
    return data

# Process datetime and index
def process_data(data):
    if data.index.tz is None:
        data.index = data.index.tz_localize('UTC')
    data.index = data.index.tz_convert('Asia/Kolkata')
    data.reset_index(inplace=True)
    if 'Date' in data.columns:
        data.rename(columns={'Date': 'Datetime'}, inplace=True)
    return data

# Calculate KPIs
def cal_metrics(data):
    last_close = float(data['Close'].iloc[-1])
    prev_close = float(data['Close'].iloc[0])
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = float(data['High'].max())
    low = float(data['Low'].min())
    vol = float(data['Volume'].sum())
    return last_close, change, pct_change, high, low, vol

# Add technical indicators
def tech_indicators(data):
    if isinstance(data['Close'], pd.DataFrame):
        close = data['Close'].squeeze()  # flatten (n,1) -> (n,)
    else:
        close = data['Close']

    # Add indicators
    data['SMA20'] = ta.trend.sma_indicator(close=close, window=20)
    data['SMA50'] = ta.trend.sma_indicator(close=close, window=50)
    data['EMA20'] = ta.trend.ema_indicator(close=close, window=20)
    data['EMA50'] = ta.trend.ema_indicator(close=close, window=50)

    return data

# ---------- STREAMLIT UI ----------

st.set_page_config(layout='wide')
st.title("📈 Stock Price Visualizer")

# Sidebar
st.sidebar.header("Chart Parameters")
ticker = st.sidebar.text_input('Ticker', 'RELIANCE.NS')
time_period = st.sidebar.selectbox('Time Period', ['1d', '1wk', '1mo', '1y', 'max'])
chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])
indicators = st.sidebar.multiselect('Technical Indicator', ['SMA20', 'SMA50', 'EMA20', 'EMA50'])

# Interval mapping
interval_map = {
    '1d': '30m',
    '1wk': '60m',
    '1mo': '1d',
    '1y': '1wk',
    'max': '1wk'
}

# Update chart when button is clicked
if st.sidebar.button('Update Parameters'):
    data = stock_data(ticker, time_period, interval_map[time_period])
    if data.empty:
        st.error(f"No data found for '{ticker}' using period '{time_period}' and interval '{interval_map[time_period]}'")
        st.stop()

    data = process_data(data)
    data = tech_indicators(data)

    # KPIs
    last_close, change, pct_change, high, low, vol = cal_metrics(data)

    st.metric(label=f"{ticker} Last Price", value=f"{last_close:.2f} INR", delta=f"{change:.2f} ({pct_change:.2f}%)")
    col1, col2, col3 = st.columns(3)
    col1.metric("High", f"{high:.2f} INR")
    col2.metric("Low", f"{low:.2f} INR")
    col3.metric("Volume", f"{vol:,}")

    # Plotting
    fig = go.Figure()

    # Candlestick or line
    if chart_type == 'Candlestick':
        fig.add_trace(go.Candlestick(
            x=data['Datetime'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            name='Candlestick'
        ))
    else:
        fig.add_trace(go.Scatter(x=data['Datetime'], y=data['Close'], mode='lines', name='Close'))

    # Indicators
    for indc in indicators:
        if indc in data.columns and data[indc].notna().any():
            fig.add_trace(go.Scatter(
                x=data['Datetime'][data[indc].notna()],
                y=data[indc][data[indc].notna()],
                name=indc
            ))

    # Safe Y-axis range
    y_min = data['Low'].min(skipna=True)
    y_max = data['High'].max(skipna=True)
    if pd.notna(y_min) and pd.notna(y_max):
        fig.update_yaxes(tickformat='.2f', range=[y_min * 0.995, y_max * 1.005])

    fig.update_layout(title=f'{ticker} {time_period.upper()} Chart',
                      xaxis_title='Time',
                      yaxis_title='Price (INR)',
                      height=600)

    st.plotly_chart(fig, use_container_width=True)

    # Show raw data
    st.subheader("📊 Historical Data")
    st.dataframe(data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']])

    st.subheader("🧮 Technical Indicators")
    st.dataframe(data[['Datetime', 'SMA20', 'SMA50', 'EMA20', 'EMA50']])
