
# Importamos las librerias
import yfinance as yf
import streamlit as st
import datetime
import pandas as pd
import cufflinks as cf

cf.go_offline()

# Definimos una función para traer la data
@st.cache_data
def get_sp500_components():
    df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    df = df[0]
    tickers = df["Symbol"].to_list()
    tickers_companies_dict = dict(
        zip(df["Symbol"], df["Security"])
    )
    return tickers, tickers_companies_dict

# Definimos una función para obtener data histórica de acciones de la bolsa
@st.cache_data
def load_data(symbol, start, end):
    return yf.download(symbol, start, end)

# Definimos una función para guardar la data como un csv file
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")

# Definimos una función para guardar la data como un csv file
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv().encode("utf-8")

# Definimos parte del sidebar que va a ser usado para seleccionar el ticker y las fechas
st.sidebar.header("Stock Parameters")
available_tickers, tickers_companies_dict = get_sp500_components()
ticker = st.sidebar.selectbox(
    "Ticker",
    available_tickers,
    format_func=tickers_companies_dict.get
)

start_date = st.sidebar.date_input(
    "Start date",
    datetime.date(2019,1,1)
)
end_date = st.sidebar.date_input(
    "End date",
    datetime.date.today()
)

if start_date > end_date:
    st.sidebar.error("The end date must fall after the start date")

# Definir la parte del sidebar usado para tunear los detalles del analysis tecnico
st.sidebar.header("Technical Analysis Parameters")
volume_flag = st.sidebar.checkbox(label="Add volume")

# Anadir el expander con parametros de la SMA
exp_sma = st.sidebar.expander("SMA")
sma_flag = exp_sma.checkbox(label ="Add SMA")
sma_periods = exp_sma.number_input(
    label="SMA Periods",
    min_value=1,
    max_value=50,
    value=20,
    step=1
)

# Anadir expander con parametros de los Bollinger bandas
exp_bb = st.sidebar.expander("Bollinger Bands")
bb_flag = exp_bb.checkbox(label="Add Bollinger Bands")
bb_periods = exp_bb.number_input(label= "BB Periods", min_value=1, max_value=50, value=20, step=1)
bb_std = exp_bb.number_input(label= "# of standard deviations", min_value=1, max_value=4, value=2, step=1)

# Anadir expander con parametros del RSI
exp_rsi = st.sidebar.expander("Relative Strength Index")
rsi_flag = exp_rsi.checkbox(label="Add RSI")
rsi_periods = exp_rsi.number_input(
    label="RSI Periods",
    min_value=1, max_value=50, value=20, step=1
)

rsi_upper = exp_rsi.number_input(label="RSI Periods", min_value=1, max_value=90, value=70, step=1)
rsi_lower = exp_rsi.number_input(label="Lower RSI", min_value=10, max_value=50, value=30, step=1)


# Especificar el titulo y texto adicional in el cuerpo principal del app
st.title("A simple web app for technical analysis")
st.subheader("User manual")
st.write( " * you can select any of the companies that is a component of the S&P index")
st.write (" * you can select the time period of your interest")
st.write (" * you can download the selected data as a CSV file")
st.write (" * you can add the following Technical Indicators to the plot: Simple Moving Average, Bollinger Bands, Relative Strength Index")
st.write (" * you can also experiment with different parameters of the indicators")


# Load the historical stock prices
df = load_data(ticker, start_date, end_date)

# Anadir el expander con la visión de la data bajada
data_exp = st.expander("Preview data")
available_cols = df.columns.tolist()
columns_to_show = data_exp.multiselect("Columns", available_cols, default=available_cols)

data_exp.dataframe(df[columns_to_show])

csv_file = convert_df_to_csv(df[columns_to_show])
data_exp.download_button(
    label="Download selected as CSV",
    data=csv_file,
    file_name=f"{ticker}_stock_prices.csv",
    mime="text/csv",
)

# Crear el candlestick chart con los TA indicadores
title_str= f"{tickers_companies_dict[ticker]} 's stock price"
qf= cf.QuantFig(df, title=title_str)
if volume_flag:
    qf.add_volume()
if sma_flag:
        qf.add_sma(periods=sma_periods)
#if bb_flag:
        #qf.add_bollinger_bands(periods= bb_periods, bollinger_bands=bb_std)
if bb_flag:
        qf.add_bollinger_bands(periods=bb_periods, boll_std=bb_std)

#qf.add_bollinger_bands(periods=bb_n,boll_std=bb_k)


if rsi_flag:
        qf.add_rsi(periods=rsi_periods, rsi_upper=rsi_upper, rsi_lower=rsi_lower,showbands=True)

fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)



