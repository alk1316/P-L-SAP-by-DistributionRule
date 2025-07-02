import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px

df = pd.read_csv('products-100.csv')

## Configuracion de Pagina
favicon = Image.open("favicon.png")
st.set_page_config(page_title='CL', page_icon=favicon, layout="wide",
                   initial_sidebar_state="collapsed")


# Funcion Streamlit
def main():
    st.title("My App")
    st.sidebar.header('Navegacion')

    st.dataframe(df)
    df_count = df.groupby('Category').count().reset_index()
    fig = px.pie(df_count, values="EAN", names='Category', title='CategoryChart')
    st.plotly_chart(fig)

    df_avg = df.groupby('Category')['Price'].mean().reset_index()
    fig2 = px.bar(df_avg, x='Category', y='Price', color="Category")
    st.plotly_chart(fig2)


if __name__== '__main__':
    main()
