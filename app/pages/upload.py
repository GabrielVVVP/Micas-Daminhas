import streamlit as st
import pandas as pd
import datetime
import time
from app.utils.helpers import get_db_connection
from app.utils.pagamentos import *

def upload():
    st.header("Upload de Arquivos")
    uploaded_file = st.file_uploader("Carregar arquivo CSV/Excel", type=["csv", "xlsx"])
    
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, skiprows=3)
        else:
            df = pd.read_excel(uploaded_file, skiprows=3)
        
        df.rename(columns={
            "D. casam.": "Data do Casamento",
            "F. pgto": "Forma de Pagamento",
            "Obs.": "Observação",
            "Auto.": "Auto",
            "T. Desc.": "Taxa de Desconto",
            "VALOR PAGO": "Valor Pago"
        }, inplace=True)

        # Convert date columns to datetime
        date_columns = ["Data", "Data do Casamento"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Converter datas na coluna "Observação"
        def converter_para_data(valor):
            try:
                return datetime.datetime.strptime(valor, "%Y-%m-%d").date().strftime("%Y-%m-%d")
            except:
                return valor

        # Check if the 'Observação' column exists before processing
        if 'Observação' in df.columns:
            df["Observação"] = df["Observação"].dropna().astype(str).apply(converter_para_data)
        if 'Valor Pago' in df.columns:
            df["Valor Pago"] = df["Valor Pago"].astype(str).str.replace(',', '.').astype(float)
        
        st.write("Prévia dos dados carregados:")
        st.dataframe(df)

        # Check for duplicates
        with get_db_connection() as conn:
            df_db = pd.read_sql("SELECT * FROM pagamentos", conn)
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df_db["Data"] = pd.to_datetime(df_db["Data"], errors='coerce')
        df["Data do Casamento"] = pd.to_datetime(df["Data do Casamento"], errors='coerce')
        df_db["Data do Casamento"] = pd.to_datetime(df_db["Data do Casamento"], errors='coerce')
        duplicates = df_db.merge(df, on=["Data", "Noiva", "Data do Casamento", "Valor", "Forma de Pagamento"], how='inner')
        
        if not duplicates.empty:
            st.warning("Existem registros duplicados no arquivo carregado.")
            st.dataframe(duplicates)
            save_button_disabled = True
        else:    
            save_button_disabled = False
        
        if st.button("Salvar no Banco de Dados", disabled=save_button_disabled):
            if duplicates.empty:
                salvar_dados_pagamentos(df)
                st.success("Dados salvos com sucesso!")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Não é possível salvar. Existem registros duplicados.")