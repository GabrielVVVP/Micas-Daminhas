import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from app.utils.participantes import get_participantes
from app.utils.pdf import exportar_pagamentos_para_pdf
from app.utils.helpers import get_db_connection, exportar_para_excel
from app.utils.caixa import carregar_dados_caixa

def display_report():

    st.header("Relatório de Clientes e Pagamentos")

    conn = get_db_connection()

    # Load data from the database
    participantes = get_participantes()

    # Update start_date and end_date to use "Data" from eventos
    min_date = pd.to_datetime(participantes["Data"], errors="coerce").min()
    max_date = pd.to_datetime(participantes["Data"], errors="coerce").max()

    # Fallback to today's date if min_date or max_date is NaT
    fallback_date = datetime.date.today()
    data_inicio = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
    data_fim = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)

    # Filtered SQL queries
    participantes = pd.read_sql_query(f"""SELECT * FROM participantes WHERE "Data" BETWEEN '{data_inicio}' AND '{data_fim}'""", conn)
    eventos_id = participantes["Evento_id"].tolist()
    if not participantes.empty:
        merged_data = []
        processed_ids = set() 
        for _id in eventos_id:
            if _id in processed_ids:
                continue 
            processed_ids.add(_id)

            evento = pd.read_sql_query(f"""SELECT "Data do Evento", "Nome", "Tipo_Evento" FROM eventos WHERE id ='{_id}'""", conn)
            orcamentos_meninas = pd.read_sql_query(f"""SELECT "Valor Total", "Valor Pago", "Tipo de Pagamento" FROM orcamentos_meninas WHERE Evento_id ='{_id}'""", conn)
            orcamentos_meninos = pd.read_sql_query(f"""SELECT "Valor Total", "Valor Pago", "Tipo de Pagamento" FROM orcamentos_meninos WHERE Evento_id ='{_id}'""", conn)

            for _, participante in participantes[participantes["Evento_id"] == _id].iterrows():
                if participante["Tipo"] == "Menina":
                    orcamento = orcamentos_meninas.iloc[0] if not orcamentos_meninas.empty else {}
                elif participante["Tipo"] == "Menino":
                    orcamento = orcamentos_meninos.iloc[0] if not orcamentos_meninos.empty else {}
                else:
                    orcamento = {}

                merged_data.append({
                    "id": participante["id"],
                    "Data": participante["Data"],
                    "Data do Evento": evento["Data do Evento"].iloc[0] if not evento.empty else None,
                    "Tipo do Evento": evento["Tipo_Evento"].iloc[0] if not evento.empty else None,
                    "Nome (Noiva ou Formando/a)": evento["Nome"].iloc[0] if not evento.empty else None,
                    "Responsável Financeiro": participante["Responsável Financeiro"],
                    "Nome (Participante)": participante["Nome"],
                    "Tipo": participante["Tipo"],
                    "Telefone": participante["Telefone"],
                    "Email": participante["Email"],
                    "Endereço": participante["Endereço"],
                    "CPF": participante["CPF"],
                    "Valor Total": orcamento.get("Valor Total"),
                    "Valor Pago": orcamento.get("Valor Pago"),
                    "Tipo de Pagamento": orcamento.get("Tipo de Pagamento")
                })

        merged_df = pd.DataFrame(merged_data)

        evento_opcoes = ["Todos"] + merged_df["Nome (Noiva ou Formando/a)"].dropna().unique().tolist()
        evento_selecionado = st.selectbox("Nome (Noiva ou Formando/a)", evento_opcoes)
        
        if evento_selecionado != "Todos":
            merged_df = merged_df[merged_df["Nome (Noiva ou Formando/a)"] == evento_selecionado]

        forma_pagamento = st.selectbox("Tipo de Pagamento", ["Todos", "Crédito + Débito", "Crédito", "Débito", "Depósito", "Dinheiro"])
        
        if forma_pagamento != "Todos":
            if forma_pagamento == "Crédito + Débito":
                merged_df = merged_df[(merged_df["Tipo de Pagamento"] == "Crédito") | (merged_df["Tipo de Pagamento"] == "Débito")]
            else:
                merged_df = merged_df[merged_df["Tipo de Pagamento"] == forma_pagamento]    

        # Botão para exportar com formatação
        if st.button("Exportar para Excel", type="primary"):
            excel_df = merged_df.drop(columns=["id","Telefone", "Email","Endereço","CPF"])
            data_start = data_inicio if data_inicio != None else datetime.datetime.today().date()
            data_end = data_fim if data_fim != None else datetime.datetime.today().date()
            file_path = "data/relatórios/CAIXA DAMINHA "+str(data_start)+" "+str(data_end)+".xlsx"
            exportar_para_excel(excel_df, file_path, data_start, data_end)
            st.success(f"Arquivo salvo como {file_path}")
            st.download_button(
                label="Baixar Excel",
                data=open(file_path, "rb").read(),
                file_name=file_path,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.dataframe(merged_df)
        st.write(f"**Número de Registros:** {len(merged_df.index)}")
    
        # Exibir somatórias conforme tipo de pagamento
        if forma_pagamento == "DEPOSITO":
            total_valor = merged_df["Valor"].sum()
            with st.container(border=True):
                st.markdown("### Balanço dos Pagamentos")
                st.write(f"**Total Valor:** R$ {total_valor:.2f}")
        elif forma_pagamento == "DINHEIRO":
            total_valor = merged_df["Valor"].sum()
            with st.container(border=True):
                st.markdown("### Balanço dos Pagamentos")
                st.write(f"**Total Valor:** R$ {total_valor:.2f}")
        elif forma_pagamento in ["CREDITO", "DEBITO", "CREDITO + DEBITO"]:
            total_valor = merged_df["Valor"].sum()
            total_valor_pago = merged_df["Valor Pago"].sum()
            diferenca = total_valor - total_valor_pago
            with st.container(border=True):
                st.markdown("### Balanço dos Pagamentos")
                st.write(f"**Total Valor:** R$ {total_valor:.2f}")
                st.write(f"**Total Valor Pago:** R$ {total_valor_pago:.2f}")
                st.write(f"**Total taxa da Máquina (Valor - Valor Pago):** R$ {diferenca:.2f}")
        else:
            total_valor_credito = merged_df[merged_df["Tipo de Pagamento"] == "Crédito"]["Valor Total"].sum()
            total_valor_pago_credito = merged_df[merged_df["Tipo de Pagamento"] == "Crédito"]["Valor Pago"].sum()
            total_valor_debito = merged_df[merged_df["Tipo de Pagamento"] == "Débito"]["Valor Total"].sum()
            total_valor_pago_debito = merged_df[merged_df["Tipo de Pagamento"] == "Débito"]["Valor Pago"].sum()
            total_valor_deposito = merged_df[merged_df["Tipo de Pagamento"] == "Depósito"]["Valor Total"].sum()
            total_valor_pago_deposito = merged_df[merged_df["Tipo de Pagamento"] == "Depósito"]["Valor Pago"].sum()
            total_valor_dinheiro = merged_df[merged_df["Tipo de Pagamento"] == "Dinheiro"]["Valor Total"].sum()     
            total_valor_pago_dinheiro = merged_df[merged_df["Tipo de Pagamento"] == "Dinheiro"]["Valor Pago"].sum()  
            
            with st.container(border=True):
                st.markdown(f"### Balanço dos Pagamentos - ({data_inicio} - {data_fim})")
                st.write(f"**Maquininha Pag Seguro Micas Virtual (Valor Total Pago com Taxas):** R$ {total_valor_credito + total_valor_debito:.2f}")
                st.write(f"**Maquininha Pag Seguro Micas Virtual (Desconto das Taxas):** R$ {(total_valor_credito + total_valor_debito) - (total_valor_pago_credito + total_valor_pago_debito):.2f}")
                st.write(f"**Maquininha Pag Seguro Micas Virtual (Valor Saldo Total sem Taxas):** R$ {total_valor_pago_credito + total_valor_pago_debito:.2f}")
                st.write(f"**Depósito Micas Virtual (Total):** R$ {total_valor_pago_deposito:.2f}")
                st.write(f"**Dinheiro (Total):** R$ {total_valor_pago_dinheiro:.2f}")
                st.write(f"**Saldo Total: R$ {total_valor_pago_credito + total_valor_pago_debito + total_valor_pago_deposito + total_valor_pago_dinheiro:.2f}**")
            
                # Create a pie chart
                pie_data = {
                    "Tipo de Pagamento": ["Crédito", "Débito", "Depósito", "Dinheiro"],
                    "Total Valor": [total_valor_pago_credito, total_valor_pago_debito, total_valor_pago_deposito, total_valor_pago_dinheiro]
                }
                pie_df = pd.DataFrame(pie_data)
                fig = px.pie(pie_df, values='Total Valor', names='Tipo de Pagamento', title='Distribuição dos Pagamentos')
                st.plotly_chart(fig)

                st.write(f"**Crédito (Saldo Total sem Taxas):** R$ {total_valor_pago_credito:.2f}")
                st.write(f"**Débito (Saldo Total sem Taxas):** R$ {total_valor_pago_debito:.2f}")
                st.write(f"**Depósito (Total):** R$ {total_valor_deposito:.2f}")
                st.write(f"**Dinheiro (Total):** R$ {total_valor_dinheiro:.2f}")

        if evento_selecionado == "Todos":
            df_retiradas = carregar_dados_caixa()
            df_retiradas = df_retiradas[df_retiradas["Operação"]=="Saída"]
            df_retiradas["Data"] = pd.to_datetime(df_retiradas["Data"], errors="coerce")
            df_retiradas = df_retiradas.dropna(subset=["Data"])
            df_retiradas = df_retiradas[(df_retiradas["Data"] >= pd.to_datetime(data_inicio)) & (df_retiradas["Data"] <= pd.to_datetime(data_fim))]
            
            total_retiradas = 0
            if not df_retiradas.empty:
                with st.container(border=True):
                    st.markdown("### Retiradas de Caixa")
                    st.dataframe(df_retiradas)
                    st.write(f"**Número de Retiradas:** {len(df_retiradas.index)}")
                    total_retiradas = df_retiradas["Valor"].sum()
                    st.write(f"**Retiradas (Total):** R$ {total_retiradas:.2f}")
            else:
                st.warning("Nenhuma retirada encontrada para o período selecionado.")

            with st.container(border=True):
                st.markdown("### Caixa Final")
                st.write(f"**Dinheiro Recebido (Total):** R$ {total_valor_dinheiro:.2f}")
                st.write(f"**Retiradas (Total):** R$ {total_retiradas:.2f}")    
                st.write(f"**Caixa do Período (Final): R$ {total_valor_dinheiro - total_retiradas:.2f}**")

        # Botão para exportar para PDF
        if st.button("Exportar para PDF"): 
            if evento_selecionado == "Todos":
                pdf_path = exportar_pagamentos_para_pdf(data_inicio, data_fim, total_valor_credito, total_valor_pago_credito, total_valor_debito, total_valor_pago_debito, total_valor_deposito, total_valor_dinheiro, total_retiradas, df_retiradas)
                st.success(f"Arquivo PDF salvo como {pdf_path}")
                st.download_button(
                    label="Baixar PDF",
                    data=open("data/balanços/"+pdf_path, "rb").read(),
                    file_name=pdf_path,
                    mime="application/pdf"
                )
            else:
                st.warning("Exportação para PDF disponível apenas para 'Todos'.")             
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")