import panel as pn
import pandas as pd
import datetime as dt

pn.extension()

# --- Cargar y preparar datos ---
df_arbol = pd.read_csv("modelo_contable_completo.txt", sep=';')
df_mov = pd.read_csv("movimientos.txt", sep=';')

df_arbol = df_arbol.rename(columns={
    'CatId': 'Numerador',
    'Name': 'Nombre',
    'Levels': 'Nivel',
    'FatherNum': 'Padre',
    'ActId': 'Codigo',
    'AcctCode': 'AcctCode',
    'AcctName': 'CuentaNombre'
})

df_arbol['Nivel'] = df_arbol['Nivel'].astype(int)
df_arbol['Padre'] = df_arbol['Padre'].fillna(-1).astype(int)
df_arbol['Numerador'] = df_arbol['Numerador'].astype(int)

df_mov['RefDate'] = pd.to_datetime(df_mov['RefDate'], errors='coerce')
df_mov['Total'] = pd.to_numeric(df_mov['Total'].astype(str).str.replace(',', ''), errors='coerce')

# --- Widgets ---
fecha_desde = pn.widgets.DatePicker(name='Desde', value=dt.date(2025, 1, 1), start=dt.date(2024, 1, 1), end=dt.date(2025, 12, 31))
fecha_hasta = pn.widgets.DatePicker(name='Hasta', value=dt.date(2025, 6, 30), start=dt.date(2024, 1, 1), end=dt.date(2025, 12, 31))
modo_vista = pn.widgets.RadioButtonGroup(name='Vista', options=['Anual', 'Trimestral', 'Mensual'], button_type='primary')
toggle_button = pn.widgets.Button(name="Expandir / Contraer", button_type="primary")

# Filtro de dimensión
valores_dimension1 = ['Todos'] + sorted(df_mov['PrcCode'].dropna().unique().tolist())
dimension1_selector = pn.widgets.Select(name='Dimension1', options=valores_dimension1)

# Estado global para expansión
expandido = {'estado': False}

# --- Función principal ---
def crear_html_arbol(df_arbol, df_mov, desde, hasta, modo, expandir=False, dimension1="Todos"):
    desde = pd.to_datetime(desde)
    hasta = pd.to_datetime(hasta)
    df_filtrado = df_mov[(df_mov['RefDate'] >= desde) & (df_mov['RefDate'] <= hasta)].copy()

    if dimension1 != "Todos":
        df_filtrado = df_filtrado[df_filtrado['PrcCode'] == dimension1]

    if modo != 'Anual':
        df_filtrado['Periodo'] = df_filtrado['RefDate'].apply(lambda x: {
            'Mensual': x.strftime('%Y-%m'),
            'Trimestral': f"{x.year}-T{((x.month - 1) // 3) + 1}"
        }[modo])
    else:
        df_filtrado['Periodo'] = 'Total'

    pivot = df_filtrado.groupby(['AcctCode', 'Periodo'])['Total'].sum().unstack(fill_value=0)

    html = "<style>details summary {cursor: pointer; font-weight: bold;} .cuenta {margin-left: 20px;}</style>"

    nivel1 = df_arbol[df_arbol['Nivel'] == 1]
    nivel2 = df_arbol[df_arbol['Nivel'] == 2]
    nivel3 = df_arbol[df_arbol['Nivel'] == 3]

    total_general = pd.Series(0, index=pivot.columns)

    for _, row1 in nivel1.iterrows():
        hijos2 = nivel2[nivel2['Padre'] == row1['Numerador']]
        total_nivel1 = pd.Series(0, index=pivot.columns)

        html_nivel1 = ""

        for _, row2 in hijos2.iterrows():
            html_nivel1 += f"<details class='cuenta'{' open' if expandir else ''}><summary>{row2['Nombre']}</summary>"
            hijos3 = nivel3[nivel3['Padre'] == row2['Numerador']]
            total_nivel2 = pd.Series(0, index=pivot.columns)

            grupos_lvl3 = hijos3.groupby(['Numerador', 'Nombre'])

            for (_, nombre), grupo in grupos_lvl3:
                grupo = grupo.copy()
                if not grupo.empty:
                    html_nivel1 += f"<details class='cuenta'{' open' if expandir else ''}><summary>{nombre}</summary>"
                    html_nivel1 += "<table style='margin-left:25px; border-collapse:collapse; margin-top:5px; font-size:13px;'>"
                    html_nivel1 += "<thead><tr>"
                    html_nivel1 += "<th style='width:140px; text-align:left; border-bottom:1px solid #ccc;'>Cuenta</th>"
                    html_nivel1 += "<th style='width:380px; max-width:380px; text-align:left; border-bottom:1px solid #ccc;'>Nombre</th>"
                    for col in pivot.columns:
                        html_nivel1 += f"<th style='min-width:90px; padding:4px 10px; text-align:right; border-bottom:1px solid #ccc;'>{col}</th>"
                    html_nivel1 += "</tr></thead><tbody>"

                    for _, row3 in grupo.iterrows():
                        acct = str(row3['AcctCode']).strip()
                        html_nivel1 += f"<tr><td style='padding:4px 8px;'>{row3['Codigo']}</td><td style='padding:4px 8px;' title='{row3['CuentaNombre']}'>{row3['CuentaNombre']}</td>"
                        for col in pivot.columns:
                            val = pivot.at[acct, col] if acct in pivot.index else 0
                            color = 'red' if val < 0 else 'black'
                            html_nivel1 += f"<td style='padding:4px 8px; text-align:right; color:{color};'>{val:,.2f}</td>"
                        html_nivel1 += "</tr>"

                    acct_codes_validos = [code for code in grupo['AcctCode'].values if code in pivot.index]
                    subtotal_row = pivot.loc[acct_codes_validos].sum()

                    html_nivel1 += "<tr><td></td><td style='text-align:right; font-weight:bold;'>Subtotal</td>"
                    for val in subtotal_row:
                        color = 'red' if val < 0 else 'black'
                        html_nivel1 += f"<td style='text-align:right; font-weight:bold; color:{color}'>{val:,.2f}</td>"
                    html_nivel1 += "</tr></tbody></table></details>"

                    total_nivel2 += subtotal_row

            if modo == 'Mensual':
                margen = 190
            elif modo == 'Trimestral':
                margen = 250
            else:
                margen = 245

            html_nivel1 += f"<table style='margin-left:{margen}px; margin-top:10px; font-size:13px; border-collapse:collapse;'>"
            html_nivel1 += "<tr>"
            html_nivel1 += f"<td style='text-align:left; font-weight:bold; min-width:300px;'>Subtotal {row2['Nombre']}</td>"
            html_nivel1 += "<td style='min-width:30px;'></td>"
            for val in total_nivel2:
                color = 'red' if val < 0 else 'green'
                html_nivel1 += f"<td style='text-align:right; font-weight:bold; color:{color}; min-width:90px; padding:0 10px'>{val:,.2f}</td>"
            html_nivel1 += "</tr></table>"

            html_nivel1 += "</details>"
            total_nivel1 += total_nivel2

        # Definir ancho por modo (en píxeles)
        if modo == 'Mensual':
            ancho_nombre = 550
            ancho_valor = 105
        elif modo == 'Trimestral':
            ancho_nombre = 570
            ancho_valor = 130
        else:  # Anual
            ancho_nombre = 570
            ancho_valor = 130

        # Construcción del grid-template-columns para el summary de Nivel 1
        num_columnas = len(pivot.columns)
        column_template = f"{ancho_nombre}px " + " ".join([f"{ancho_valor}px"] * num_columnas)

        html += f"<details{' open' if expandir else ''}><summary style='display: grid; grid-template-columns: {column_template}; align-items: center;'>"

        # Nombre fijo del bloque
        html += f"<span style='overflow:hidden; white-space:nowrap; text-overflow:ellipsis; font-weight:bold;'>{row1['Nombre']}</span>"

        # Valores alineados
        for val in total_nivel1:
            color = 'red' if val < 0 else 'green'
            html += f"<span style='text-align:right; color:{color}; font-weight:bold;'>{val:,.2f}</span>"

        html += "</summary>"

        html += html_nivel1

        if modo == 'Mensual':
            margen_total = 240
        elif modo == 'Trimestral':
            margen_total = 250
        else:
            margen_total = 245

        html += f"<table style='margin-left:{margen_total}px; margin-top:10px; font-size:15px; border-collapse:collapse;'>"
        html += "<tr>"
        html += f"<td style='text-align:left; font-weight:bold; min-width:300px;'>Total {row1['Nombre']}</td>"
        html += "<td style='width:50px;'></td>"
        for val in total_nivel1:
            color = 'red' if val < 0 else 'green'
            html += f"<td style='text-align:right; font-weight:bold; color:{color}; min-width:90px; padding:0 10px'>{val:,.2f}</td>"
        html += "</tr></table></details>"

        total_general += total_nivel1

    # Ganancia / Pérdida final
    if modo == 'Mensual':
        margen_total = 240
    elif modo == 'Trimestral':
        margen_total = 250
    else:
        margen_total = 245

    html += "<hr style='margin-top:30px; margin-bottom:10px;'>"
    html += f"<table style='margin-left:{margen_total}px; margin-top:10px; font-size:16px; font-weight:bold; border-collapse:collapse;'>"
    html += "<tr>"
    html += "<td style='text-align:left; min-width:300px;'>Ganancia / Pérdida</td>"
    html += "<td style='width:50px;'></td>"
    for val in total_general:
        color = 'red' if val < 0 else 'green'
        html += f"<td style='text-align:right; color:{color}; min-width:90px; padding:0 15px'>{val:,.2f}</td>"
    html += "</tr></table>"

    return html




# Panel HTML
html_pane = pn.pane.HTML(height_policy="auto", sizing_mode="stretch_width")

# Actualizar HTML dinámicamente
def actualizar_html(event=None):
    html_str = crear_html_arbol(
        df_arbol,
        df_mov,
        fecha_desde.value,
        fecha_hasta.value,
        modo_vista.value,
        expandir=expandido['estado'],
        dimension1=dimension1_selector.value
    )
    html_pane.object = html_str


# Watchers
fecha_desde.param.watch(lambda e: actualizar_html(), 'value')
fecha_hasta.param.watch(lambda e: actualizar_html(), 'value')
modo_vista.param.watch(lambda e: actualizar_html(), 'value')
dimension1_selector.param.watch(lambda e: actualizar_html(), 'value')

# Botón expandir / contraer
def toggle_expandir(event):
    expandido['estado'] = not expandido['estado']
    actualizar_html()

toggle_button.on_click(toggle_expandir)

# Layout
layout = pn.template.MaterialTemplate(
    title="Árbol del Plan de Cuentas",
    sidebar=[fecha_desde, fecha_hasta, modo_vista, dimension1_selector, toggle_button],
    main=[html_pane]
)

# Inicial
actualizar_html()
layout.servable()
