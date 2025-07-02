import streamlit as st
import pandas as pd
from PIL import Image

df = pd.read_csv('products-100.csv')

def main():

    st.title("Curso Streamlit")
    st.header("Dataframe: ")
    st.dataframe(df)
    # st.write(df.head())
    #st.json()

    codigo = ''' 
    Select * from OITM
            '''
    st.code(codigo, language="sql")

    # Selectbox
    opcion1 = st.selectbox(
        "Elige tu fruta favorita",
        ['manzana', 'platano', 'freza']
    )

    st.write(f"tu fruta favorita es: {opcion1}")


    opciones = st.multiselect(
        "Selecciona tus colores favoritos:",
        ['rojo', 'azul', 'verde', 'amarillo']
    )

    st.write(f"tus colores favoritos son: {opciones}")

    #Slider:
    edad = st.slider(
        'Selecciona tu edad:',
        min_value= 1,
        max_value=100,
        value=18,
        step=1
    )

    st.write(f'Tu edad es: {edad}')

    # Select Slider:
    nivel = st.select_slider(
        'Nivel de satisfaccion:',
        options=['Muy bajo', 'Bajo', 'Medio', 'Alto', 'Muy Malo'],
        value='Medio'
    )

    st.write(f"tu nivel de satisfaccion:{nivel}")

    img = Image.open("Jireh-CEO.PNG")
    st.image(img, use_container_width=True)

    nombre = st.text_input("Ingresa nombre")
    st.write(nombre)

    mensaje = st.text_area("Ingresa un detalle", height=100)
    st.write(mensaje)

    numero = st.number_input("Ingresa numero", 1, 25, step=1)

    fecha = st.date_input("Ingresa fecha:")
    st.write(f"su fecha es {fecha}")



if __name__ == "__main__":
    main()



