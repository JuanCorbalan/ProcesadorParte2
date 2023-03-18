import pandas as pd
import streamlit as st
from collections import Counter

def post_process(df_filtrado, df_sacado):
    df_filtrado_sin_null = df_filtrado.dropna(subset = ['Size'])
    df_filtrado_sin_null = df_filtrado_sin_null[df_filtrado_sin_null['Color'] > 1]
    nulls = df_filtrado['Size'].isna()
    df_filtrado_con_null = df_filtrado[nulls]
    df_filtrado_con_null['Size'] = df_filtrado_con_null['Color']
    df_filtrado_con_null= df_filtrado_con_null.drop('Color',axis=1)
    res = pd.concat([df_sacado, df_filtrado_con_null])
    res = res.sort_values(by='Size',ascending=False)

    return res,df_filtrado_sin_null


def resolutor(df_datos_contados, df_visualizado, selected_dic,dicc):

    df_visualizado['Categorias'] = df_visualizado['Categorias'].str.lower()

    df_visualizado['Color'] = df_visualizado['Categorias'].map(selected_dic)

    df_merged_data = pd.merge(df_visualizado,df_datos_contados,on = 'Text',how= 'left')

    del df_merged_data['Categorias']

    df_merged_data['Color'],df_merged_data['Size'] = df_merged_data['Size'],df_merged_data['Color']

    df_merged_data.head()

    return df_merged_data

def ver_descarte(df_datos_contados,df_visualizado,df_palabras_a_sacar):
    df_sin_compartidos = pd.concat([df_visualizado,df_datos_contados])

    df_sin_compartidos = df_sin_compartidos.drop_duplicates(['Text'],keep=False)

    del df_sin_compartidos['Categorias']
    del df_sin_compartidos['Color']

    df_sin_compartidos2 = pd.concat([df_sin_compartidos,df_palabras_a_sacar])

    df_sin_compartidos2 = df_sin_compartidos2.drop_duplicates(['Text'],keep=False)

    df_sin_compartidos2.sort_values(by='Size', inplace=True,ascending=False)
    df_sin_compartidos2 = df_sin_compartidos2[~df_sin_compartidos2['Text'].str.startswith('Https')]
    
    

    return df_sin_compartidos2

# Define your script here
def process_csvs(df_datos_contados, df_visualizado, df_palabras_a_sacar,dic,dicc):
    filtered_df = resolutor(df_datos_contados, df_visualizado,dic,dicc)
    removed_data= ver_descarte(df_datos_contados,df_visualizado, df_palabras_a_sacar)
    return filtered_df, removed_data

def contarPalabras(df_datos_crudos):
    aux = df_datos_crudos['Content'].str.cat(sep = ' ')
    word_list = aux.lower().split()
    word_counts = Counter(word_list)

    df_word_counts = pd.DataFrame.from_dict(word_counts, orient='index', columns=['Size'])

    # reset the index and rename the columns
    df_word_counts.reset_index(inplace=True)
    df_word_counts.rename(columns={'index': 'Text'}, inplace=True)
    df_word_counts['Text'] = df_word_counts['Text'].str.title()

    return df_word_counts




def main():
    st.set_page_config(page_title="Procesador de Datos", page_icon=":guardsman:", layout="wide",initial_sidebar_state="expanded")
    st.title("Bienvenido al procesador de datos para escucha en redes")
    st.subheader("La idea de esta web app es procesar la informacion un archivo xlsx. Se contabiliza la aparicion de cada palabra y luego ciertas palabras seleccionadas son mostradas para que se visualizen junto a sus apariciones y un color asignado para luego utilizarlo en WordArt")

    dic_options = ['Sentimientos', 'Tematicas']
    selected_dic = st.selectbox("Elegir de que forma se van aprocesar los datos", dic_options)

    dic = {}
    dicc = pd.read_csv(f'{selected_dic}.csv')

    for index, row in dicc.iterrows():
        entrada = row['Categoria'].lower()
        definicion = row['Color']
        dic[entrada] = definicion
            
    for key, value in dic.items():
        st.write(f"<p style='color:#{value};font-size: 24px;display: inline;'>{key}</p>", unsafe_allow_html=True)
    
    st.subheader("Para agregar una categoria")
    color = st.color_picker('Elegir un color', '#ff0000')
    user_input = st.text_input("Elegir un nombre")
    if st.button("Agregar como categoria"):
        color = color[1:]
        dic[user_input] = color
        new_row = pd.DataFrame({'Categoria':[user_input],'Color':[color]}) 
        dicc = dicc.append(new_row)
        dicc.to_csv(f'{selected_dic}.csv',index=False)
        for key, value in dic.items():
            st.write(f"<p style='color:#{value};font-size: 24px;display: inline;'>{key}</p>", unsafe_allow_html=True)
    st.subheader("Para sacar de forma permanente una categoria")
    selected_element = st.selectbox("Seleccione uno para sacar",dicc['Categoria'])
    st.write("Vas a sacar: ", selected_element)
    if st.button("Sacar como categoria"):
        dicc = dicc.drop(dicc.loc[dicc['Categoria']==selected_element].index)
        dicc.to_csv(f'{selected_dic}.csv',index=False)
        del dic[selected_element]
        for key, value in dic.items():
            st.write(f"<p style='color:#{value};font-size: 24px;display: inline;'>{key}</p>", unsafe_allow_html=True)
    
    st.subheader("Para seleccionar unas categorias")
    
    opciones_categorias = dicc['Categoria']
    categorias_seleccionadas = st.multiselect('Selecciona las categorías', opciones_categorias)

    df_filtra = dicc[dicc['Categoria'].isin(categorias_seleccionadas)]

    if st.button("Quedarse con estas categorias"):
        dic.clear()
        dicc = df_filtra
        df_filtra.to_csv(f'{selected_dic}f.csv',index=False)

    if st.button("Quedarse con todas las categorias"):
        dicc.to_csv(f'{selected_dic}f.csv',index=False)

    
    dic.clear()

    dicc = pd.read_csv(f'{selected_dic}f.csv')
    for index, row in dicc.iterrows():
        entrada = row['Categoria'].lower()
        definicion = row['Color']
        dic[entrada] = definicion
            

    
    

    st.dataframe(dicc)

    uploaded_file1 = st.file_uploader("Primero el excel con datos crudos", type=["xlsx"])
    uploaded_file2 = st.file_uploader("Segundo el filtrador de datos", type=["xlsx"])
    uploaded_file3 = st.file_uploader("Tercero palabras a sacar", type=["xlsx"])

    b = st.button("Empezar filtrado")
    if uploaded_file1 and uploaded_file2 and uploaded_file3 and b:
        df_datos_crudos = pd.read_excel(uploaded_file1)
        df_datos_contados = contarPalabras(df_datos_crudos)
        df_visualizado = pd.read_excel(uploaded_file2)
        df_palabras_a_sacar = pd.read_excel(uploaded_file3)
        filtered_df, removed_data = process_csvs(df_datos_contados, df_visualizado, df_palabras_a_sacar,dic,dicc)
        removed_data,filtered_df = post_process(filtered_df,removed_data)
        st.subheader("Algunas palabras que no entraron: ")
        removed_data = removed_data.reset_index()
        del removed_data['index']
        st.dataframe(removed_data.head(150).style.set_properties(**{'text-align': 'left'}).format({'Size': '{:,.0f}'}),width=300)

        st.subheader("Primeras 250 no @ que no entraron: ")
        removed_data2 = removed_data[~removed_data['Text'].str.startswith('@')]
        removed_data2 = removed_data2.reset_index()
        del removed_data2['index']
        del removed_data2['level_0']
        st.dataframe(removed_data2.head(250).style.format({'Size': '{:,.0f}'}),width=300)
    
        
        st.subheader("Primeros 70 @ que no entraron: ")
        removed_data3 = removed_data[removed_data['Text'].str.startswith('@')]
        removed_data3 = removed_data3.reset_index()
        del removed_data3['index']
        del removed_data3['level_0']
        st.dataframe(removed_data3.head(70).style.set_properties(**{'text-align': 'left'}).format({'Size': '{:,.0f}'}),width=300)
    
        st.title("Poner en el word art: ")
        filtered_df = filtered_df.rename(columns={'Color':'Cantidad', 'Size':'Color'})

        st.table(filtered_df.reset_index(drop=True).style.set_table_styles([
            {'selector': 'table', 'props': [('border', '2px solid black'),
                                            ('text-align', 'center'),
                                            ('font-size', '20px'),
                                            ('background-color', 'white')]},
            {'selector': 'th', 'props': [('display','none')]},
            {'selector': 'td', 'props': [('border', '2px solid black'),
                                            ('background-color', 'white')]},
        ]))


        color_size_sum = filtered_df.groupby('Color')['Cantidad'].sum()

        color_map=dict(zip(dicc['Color'],dicc['Categoria']))

        color_size_sum = color_size_sum.rename(color_map)

        st.subheader("Algunas estadisticas: ")
        color_size_sum_df = pd.DataFrame(color_size_sum)
        color_size_sum_df["Porcentajes"]  = color_size_sum_df["Cantidad"].div(color_size_sum_df["Cantidad"].sum())*100
        st.table(color_size_sum_df.style.format({'Cantidad': '{:,.0f}','Porcentajes':'{:.2f}%'}).set_table_styles([
            {'selector': 'table', 'props': [('border', '2px solid black'),
                                            ('text-align', 'center'),
                                            ('font-size', '20px'),
                                            ('background-color', 'white')]},
            {'selector': 'th', 'props': [('border', '2px solid black'),
                                            ('background-color', 'white')]},
            {'selector': 'td', 'props': [('border', '2px solid black'),
                                            ('background-color', 'white')]},
        ]))




main()
