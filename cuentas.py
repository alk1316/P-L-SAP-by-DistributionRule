import streamlit as st
import pandas as pd

st.set_page_config(page_title="Árbol del Plan de Cuentas", layout="wide")
st.title("Árbol del Plan de Cuentas")

# Cargar el archivo fijo
df = pd.read_csv('modelo_contable_completo.txt', sep=';')

# Renombrar columnas
df = df.rename(columns={
    'CatId': 'Numerador',
    'Name': 'Nombre',
    'Levels': 'Nivel',
    'FatherNum': 'Padre',
    'ActId': 'Codigo'
})

# Convertir tipos
df['Nivel'] = df['Nivel'].astype(int)
df['Padre'] = df['Padre'].fillna(-1).astype(int)
df['Numerador'] = df['Numerador'].astype(int)

# Separar por niveles
nivel1 = df[df['Nivel'] == 1]
nivel2 = df[df['Nivel'] == 2]
nivel3 = df[df['Nivel'] == 3]

# Mostrar estructura
for _, row1 in nivel1.iterrows():
    st.markdown(f"## {row1['Nombre']}")
    hijos_nivel2 = nivel2[nivel2['Padre'] == row1['Numerador']]
    for _, row2 in hijos_nivel2.iterrows():
        st.markdown(f"### &emsp;└─ {row2['Nombre']}")

        # 👉 Agrupar por Nombre y Numerador (para que no se repita título)
        hijos_nivel3 = nivel3[nivel3['Padre'] == row2['Numerador']]
        grupos_nivel3 = hijos_nivel3.groupby(['Numerador', 'Nombre'])

        for (_, nombre), grupo in grupos_nivel3:
            st.markdown(f"#### &emsp;&emsp;• {nombre}")
            for _, row3 in grupo.iterrows():
                if pd.notnull(row3['Codigo']):
                    st.markdown(f"&emsp;&emsp;&emsp;&emsp;- `{row3['Codigo']}`")


