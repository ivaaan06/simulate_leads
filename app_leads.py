import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Asignador Inteligente de Leads")
leads_file = st.file_uploader("Carga archivo de Leads (CSV)", type="csv")


st.subheader("Asignación automática de leads")

if leads_file :
    number_tope = st.number_input("Inserte el valor de topes de asignación", min_value=0, value=10)
    if number_tope > 0:
        df_asesor = pd.read_csv('asesor_profiles.csv')
        df_leads = pd.read_csv(leads_file)
        df_leads['created'] = pd.to_datetime(df_leads['created'])
        cant_days = df_leads['created'].dt.date.nunique()

        number_tope =  number_tope * cant_days

        col1, col2 = st.columns(2)
        with col1:
            st.write("Leads cargados:")
            st.dataframe(df_leads)
        with col2:
            st.write("Asesores:")
            st.dataframe(df_asesor)

        source_score_map = {
        'referral': 10, 'adwords': 10, 'facebook': 5, 'google': 7
        }
        medium_score_map = {
            'cpc': 10, 'organic': 7, 'customer_network': 7, 'affiliates': 5
        }

        #calculate scores based on source and medium
        df_leads['source_score'] = df_leads['source'].map(source_score_map).fillna(3)  
        df_leads['medium_score'] = df_leads['medium'].map(medium_score_map).fillna(3)  
        df_leads['total_score'] = df_leads['source_score'] + df_leads['medium_score']

        # Classify leads based on total_score leads priorities
        condition_group_a = (df_leads['total_score'] > 15)
        condition_group_b = (df_leads['total_score'] >= 12) & (df_leads['total_score'] <= 15)
        condition_group_c = (df_leads['total_score'] < 12)

        #Initial classification
        df_leads.loc[condition_group_a, 'group'] = 'A'
        df_leads.loc[condition_group_b, 'group'] = 'B'
        df_leads.loc[condition_group_c, 'group'] = 'C'

        #create groups based on profile
        group_a = df_asesor[df_asesor['profile'] == 'Senior']
        group_b = df_asesor[df_asesor['profile'] == 'Junior']
        group_c = df_asesor[df_asesor['profile'] == 'Nuevo']   

        #Crear ciclo rotativo 
        ciclo_a = cycle(group_a['id_asesor'].tolist())
        ciclo_b = cycle(group_b['id_asesor'].tolist())
        ciclo_c = cycle(group_c['id_asesor'].tolist())

        # Diccionarios rápidos para acceso y conteo
        conteo_a = dict.fromkeys(group_a['id_asesor'], 0)
        conteo_b = dict.fromkeys(group_b['id_asesor'], 0)
        conteo_c = dict.fromkeys(group_c['id_asesor'], 0)


        df_leads_asigned_a = []
        df_leads_asigned_b = []
        df_leads_asigned_c = []

        df_leads['id_advisor_assigned'] = None

        for idx, row in df_leads.iterrows():
            if row['group'] == 'A':
                for _ in range(len(conteo_a)):
                    asesor = next(ciclo_a)
                    if conteo_a[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        conteo_a[asesor] += 1
                        break

            elif row['group'] == 'B':
                for _ in range(len(conteo_b)):
                    asesor = next(ciclo_b)
                    if conteo_b[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        conteo_b[asesor] += 1
                        break

            elif row['group'] == 'C':
                for _ in range(len(conteo_c)):
                    asesor = next(ciclo_c)
                    if conteo_c[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        conteo_c[asesor] += 1
                        break


        st.write("Grupos, primer condicional Prioridad leads")
        df_leads_order = df_leads.sort_values(by='group', ascending=True)
        st.dataframe(df_leads_order)


        #second condition score total
        condition_group_a_secundary = (df_leads['total_score'] >= 14) & (df_leads['total_score'] <= 15) & (df_leads['id_advisor_assigned'] is None )  
        condition_group_b_secundary = (df_leads['total_score'] >= 10) & (df_leads['total_score'] <= 11) & (df_leads['id_advisor_assigned'] is None )
        condition_group_c_secundary = (df_leads['total_score'] >= 10) & (df_leads['total_score'] <= 11) & (df_leads['id_advisor_assigned'] is None )

        df_leads.loc[condition_group_a, 'group'] = 'A'
        df_leads.loc[condition_group_b, 'group'] = 'B'
        df_leads.loc[condition_group_c, 'group'] = 'C'

        #Reset count
        conteo_a = dict.fromkeys(group_a['id_asesor'], 0)
        conteo_b = dict.fromkeys(group_b['id_asesor'], 0)
        conteo_c = dict.fromkeys(group_c['id_asesor'], 0)
        
        for idx, row in df_leads.iterrows():
            if row['group'] == 'A' and row['id_advisor_assigned'] is None:
                for _ in range(len(conteo_a)):
                    asesor = next(ciclo_a)
                    if conteo_a[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        conteo_a[asesor] += 1
                        break

            elif row['group'] == 'B' and row['id_advisor_assigned'] is None:
                for _ in range(len(conteo_b)):
                    asesor = next(ciclo_b)
                    if conteo_b[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        conteo_b[asesor] += 1
                        break

            elif row['group'] == 'C' and row['id_advisor_assigned'] is None:
                for _ in range(len(conteo_c)):
                    asesor = next(ciclo_c)
                    if conteo_c[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        conteo_c[asesor] += 1
                        break


        st.write("Grupos, segundo condicional Prioridad leads")
        df_leads_order_2 = df_leads.sort_values(by='group', ascending=True)
        st.dataframe(df_leads_order_2)

        ############# Asignacion en cascada ###################################
        
        # Asignar leads no asignados en cascada (A->B->C)
        for idx, row in df_leads.iterrows():
            if row['id_advisor_assigned'] is None:
                # Intentar asignar a grupo A primero
                assigned = False
                for _ in range(len(conteo_a)):
                    asesor = next(ciclo_a)
                    if conteo_a[asesor] < number_tope:
                        df_leads.at[idx, 'id_advisor_assigned'] = asesor
                        df_leads.at[idx, 'group'] = 'A'
                        conteo_a[asesor] += 1
                        assigned = True
                        break
                
                if not assigned:
                    for _ in range(len(conteo_b)):
                        asesor = next(ciclo_b)
                        if conteo_b[asesor] < number_tope:
                            df_leads.at[idx, 'id_advisor_assigned'] = asesor
                            df_leads.at[idx, 'group'] = 'B'
                            conteo_b[asesor] += 1
                            assigned = True
                            break
                
                # Si no se pudo asignar a B, intentar con C
                if not assigned:
                    for _ in range(len(conteo_c)):
                        asesor = next(ciclo_c)
                        if conteo_c[asesor] < number_tope:
                            df_leads.at[idx, 'id_advisor_assigned'] = asesor
                            df_leads.at[idx, 'group'] = 'C'
                            conteo_c[asesor] += 1
                            break

        ############# Asignacion Aleatoria ###################################
        
        # Asignar leads restantes de forma aleatoria si todos los asesores están llenos
        import random
        
        for idx, row in df_leads.iterrows():
            if row['id_advisor_assigned'] is None:
                # Si no se pudo asignar por capacidad, asignar aleatoriamente
                all_asesores = df_asesor['id_asesor'].tolist()
                random_asesor = random.choice(all_asesores)
                df_leads.at[idx, 'id_advisor_assigned'] = random_asesor

                if df_asesor.loc[df_asesor['id_asesor'] == random_asesor, 'profile'].values[0] == 'Senior': 
                    df_leads.at[idx, 'group'] = 'A' 
                elif df_asesor.loc[df_asesor['id_asesor'] == random_asesor, 'profile'].values[0] == 'Junior': 
                    df_leads.at[idx, 'group'] = 'B' 
                else:
                    df_leads.at[idx, 'group'] = 'C' 
                 


        st.write("Asignación final de leads")
        st.dataframe(df_leads)




        st.subheader("Asesores vs Leads")
        x = df_asesor['name_asesor'].values
        y = df_leads['id_advisor_assigned'].value_counts().reindex(df_asesor['id_asesor']).fillna(0).astype(int).values
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x=x, height=y, width=0.6) 
        bars = ax.bar(x=x, height=y, color='#1f77b4', width=0.6, edgecolor='white')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), 
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

        ax.set_xticklabels(x, rotation=45, ha='right', fontsize=9)
        fig.tight_layout()
        st.pyplot(fig)


        st.subheader("Grupos vs Leads")
        x = ['A','B','C']
        y = df_leads[df_leads['id_advisor_assigned'].notna()]['group'].value_counts().reindex(['A','B','C']).fillna(0).values
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x=x, height=y, width=0.6) 
        bars = ax.bar(x=x, height=y, color='#1f77b4', width=0.6, edgecolor='white')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)

        ax.set_xticklabels(x, rotation=45, ha='right', fontsize=9)
        fig.tight_layout()
        st.pyplot(fig)


        st.subheader("Leads")
        plt.figure(figsize=(10, 6))
        sns.stripplot(
            data=df_leads,
            x='total_score',
            y='group',
            jitter=True,
            palette='Set2',
            alpha=0.8
        )
        plt.title("Dispersión de Leads Asignados")
        plt.xlabel("Score del Lead")
        plt.ylabel("Grupo Asignado")
        plt.grid(True, axis='x', linestyle='--', alpha=0.5)
        st.pyplot(plt)
