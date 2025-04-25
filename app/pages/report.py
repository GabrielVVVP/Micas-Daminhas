import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from app.utils.eventos import get_eventos_param_by_ids
from app.utils.participantes import get_participantes
from app.utils.pdf import exportar_pagamentos_para_pdf
from app.utils.helpers import exportar_para_excel, ensure_month_year_folder
from app.utils.caixa import carregar_dados_caixa
from app.utils.pagamentos import get_pagamentos_eventos
from app.utils.orcamentos import get_orcamentos_param_by_ids

def display_report():

    st.header("Relatório de Pagamentos")

    # Load data from the database
    participantes = get_participantes()

    # Update start_date and end_date to use "Data" from eventos
    fallback_date = datetime.date.today()
    min_date = pd.to_datetime(participantes["Data"], errors="coerce").min()
    max_date = pd.to_datetime(participantes["Data"], errors="coerce").max()

    # Replace buttons with a select box for date range selection
    date_option = st.selectbox("Selecione o período", ["Dia", "Mês", "Ano", "Seletor de Datas"], index=1)

    if date_option == "Dia":
        start_date = datetime.date.today()
        end_date = datetime.date.today()
    elif date_option == "Mês":
        start_date = datetime.date.today().replace(day=1)
        end_date = (datetime.date.today().replace(day=1) + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(days=1)
    elif date_option == "Ano":
        start_date = datetime.date.today().replace(month=1, day=1)
        end_date = datetime.date.today().replace(month=12, day=31)
    elif date_option == "Seletor de Datas":
        start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
        end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)

    # Filtered SQL queries
    pagamentos = get_pagamentos_eventos(start_date, end_date)
    eventos_id = pagamentos["Evento_id"].dropna().unique().tolist()
    eventos_nomes = get_eventos_param_by_ids(eventos_id, "Nome")
    eventos_dict = dict(zip(eventos_id, eventos_nomes))
    orcamentos_meninos, orcamentos_meninas = get_orcamentos_param_by_ids(eventos_id)
    if not pagamentos.empty:
        merged_data = []
        processed_ids = set() 
        for _id in eventos_id:
            if _id in processed_ids:
                continue 
            processed_ids.add(_id)

            orcamento_meninos_evento = orcamentos_meninos[orcamentos_meninos["Evento_id"] == _id]
            orcamento_meninas_evento = orcamentos_meninas[orcamentos_meninas["Evento_id"] == _id]

            # Check Tipo Pagamento for the event
            tipo_pagamento_evento = pagamentos[pagamentos["Evento_id"] == _id]["Tipo Pagamento"].iloc[0]

            for _, pagamento in pagamentos[pagamentos["Evento_id"] == _id].iterrows():

                # Determine the orcamento source based on Tipo of Participante
                if pd.notna(pagamento["Participante_id"]):
                    valor_total = 0
                    valor_com_desconto = 0

                    participante_data = participantes[participantes["id"] == pagamento["Participante_id"]]
        
                    if not participante_data.empty:
                        participante_tipo = participante_data["Tipo"].iloc[0]
                        if participante_tipo == "Menina":
                            orcamento = orcamento_meninas_evento[orcamento_meninas_evento["Participante_id"] == pagamento["Participante_id"]]
                        elif participante_tipo == "Menino":
                            orcamento = orcamento_meninos_evento[orcamento_meninos_evento["Participante_id"] == pagamento["Participante_id"]]
                        else:
                            orcamento = None

                        valor_total = orcamento["Valor Total"].iloc[0] if not orcamento.empty else 0
                        valor_com_desconto = orcamento["Valor com Desconto"].iloc[0] if not orcamento.empty else 0
                else:
                    # For Cliente Integral, sum all values from both orcamentos
                    if tipo_pagamento_evento == "Cliente Integral":
                        valor_total = orcamento_meninos_evento["Valor Total"].sum() + orcamento_meninas_evento["Valor Total"].sum()
                        valor_com_desconto = orcamento_meninos_evento["Valor com Desconto"].sum() + orcamento_meninas_evento["Valor com Desconto"].sum()
                    else:
                        valor_total = 0
                        valor_com_desconto = 0
                
                participante_data = participantes[participantes["id"] == pagamento["Participante_id"]]
                if not participante_data.empty:
                    nome_participante = participante_data.iloc[0]["Nome"]
                else:
                    nome_participante = "Todos do Evento"
                
                merged_data.append({
                    "id": pagamento["id"],
                    "Data do Pagamento": pagamento["Data do Pagamento"],
                    "Data do Evento": pagamento["Data do Evento"] if not pagamento.empty else None,
                    "Tipo do Evento": pagamento["Tipo Evento"] if not pagamento.empty else None,
                    "Nome (Noiva ou Formando/a)":  eventos_dict.get(_id, None),
                    "Nome (Participante)": nome_participante,
                    "Tipo de Pagamento": pagamento["Tipo Pagamento"],
                    "Forma de Pagamento": pagamento["Forma de Pagamento"],  
                    "Valor Total": valor_total,
                    "Valor com Desconto": valor_com_desconto,
                    "Valor Pago": pagamento["Valor Pago"],
                    "Taxa da Máquina": pagamento["Taxa da Máquina"],
                    "Valor Recebido": pagamento["Valor Recebido"],
                    "Valor Restante": 0,
                    "Observação": pagamento["Observação"],
                    "Status": pagamento["Status"]
                })

        merged_df = pd.DataFrame(merged_data)
        if not merged_df.empty:
            # Create a new column to track changes in "Nome (Noiva ou Formando/a)" and "Nome (Participante)"
            merged_df["Group Key"] = merged_df.apply(
                lambda row: row["Nome (Noiva ou Formando/a)"] if row["Tipo de Pagamento"] == "Cliente Integral" else f"{row['Nome (Noiva ou Formando/a)']} - {row['Nome (Participante)']}",
                axis=1
            )

            # Calculate cumulative sum and Valor Restante based on the "Group Key"
            merged_df["Cumulative Valor Recebido"] = merged_df.groupby("Group Key")["Valor Recebido"].cumsum()

            # Calculate Valor Restante
            merged_df["Valor Restante"] = merged_df["Valor com Desconto"] - merged_df["Cumulative Valor Recebido"]

            # Drop the temporary "Group Key" column
            merged_df.drop(columns=["Group Key","Cumulative Valor Recebido"], inplace=True)

        evento_opcoes = ["Todos"] + merged_df["Nome (Noiva ou Formando/a)"].dropna().unique().tolist()
        evento_selecionado = st.selectbox("Nome (Noiva ou Formando/a)", evento_opcoes)
        
        if evento_selecionado != "Todos":
            merged_df = merged_df[merged_df["Nome (Noiva ou Formando/a)"] == evento_selecionado]

        forma_pagamento = st.selectbox("Forma de Pagamento", ["Todos", "Crédito + Débito", "Crédito", "Débito", "Depósito", "Dinheiro"])
        
        if forma_pagamento != "Todos":
            if forma_pagamento == "Crédito + Débito":
                merged_df = merged_df[(merged_df["Forma de Pagamento"] == "Crédito") | (merged_df["Forma de Pagamento"] == "Débito")]
            else:
                merged_df = merged_df[merged_df["Forma de Pagamento"] == forma_pagamento]    

        # Botão para exportar com formatação
        if st.button("Exportar para Excel", type="primary"):
            excel_df = merged_df.copy()
            columns_to_drop = ["id", "Nome (Participante)", "Tipo de Pagamento", "Valor Total", "Valor com Desconto", "Valor Restante", "Status"]
            existing_columns = [col for col in columns_to_drop if col in excel_df.columns]
            excel_df = excel_df.drop(columns=existing_columns)
            data_start = start_date if start_date != None else datetime.datetime.today().date()
            data_end = end_date if end_date != None else datetime.datetime.today().date()
            file_path = "data/caixa/"
            base_path = ensure_month_year_folder(file_path,data_end)
            file_path = base_path+"/CAIXA DAMINHA "+str(data_start)+" "+str(data_end)+".xlsx"
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
        total_valor_dinheiro = merged_df[merged_df["Forma de Pagamento"] == "Dinheiro"]["Valor Total"].sum()  
    
        # Exibir somatórias conforme tipo de pagamento
        if forma_pagamento == "Depósito":
            total_valor = merged_df["Valor Total"].sum()
            with st.container(border=True):
                st.markdown(f"### Balanço dos Pagamentos - ({start_date} - {end_date})")
                st.write(f"**Total Valor:** R$ {total_valor:.2f}")
        elif forma_pagamento == "Dinheiro":
            total_valor = merged_df["Valor Total"].sum()
            with st.container(border=True):
                st.markdown(f"### Balanço dos Pagamentos - ({start_date} - {end_date})")
                st.write(f"**Total Valor:** R$ {total_valor:.2f}")
        elif forma_pagamento in ["Crédito", "Débito", "Crédito + Débito"]:
            total_valor = merged_df["Valor Total"].sum()
            total_valor_pago = merged_df["Valor Pago"].sum()
            diferenca = total_valor - total_valor_pago
            with st.container(border=True):
                st.markdown(f"### Balanço dos Pagamentos - ({start_date} - {end_date})")
                st.write(f"**Total Valor:** R$ {total_valor:.2f}")
                st.write(f"**Total Valor Pago:** R$ {total_valor_pago:.2f}")
                st.write(f"**Total taxa da Máquina (Valor - Valor Pago):** R$ {diferenca:.2f}")
        else:
            total_valor_credito = merged_df[merged_df["Forma de Pagamento"] == "Crédito"]["Valor Total"].sum()
            total_valor_pago_credito = merged_df[merged_df["Forma de Pagamento"] == "Crédito"]["Valor Recebido"].sum()
            total_valor_taxa_maquina = merged_df[merged_df["Forma de Pagamento"] == "Crédito"]["Taxa da Máquina"].sum()
            total_valor_debito = merged_df[merged_df["Forma de Pagamento"] == "Débito"]["Valor Total"].sum()
            total_valor_pago_debito = merged_df[merged_df["Forma de Pagamento"] == "Débito"]["Valor Recebido"].sum()
            total_valor_deposito = merged_df[merged_df["Forma de Pagamento"] == "Depósito"]["Valor Total"].sum()
            total_valor_pago_deposito = merged_df[merged_df["Forma de Pagamento"] == "Depósito"]["Valor Pago"].sum()   
            total_valor_pago_dinheiro = merged_df[merged_df["Forma de Pagamento"] == "Dinheiro"]["Valor Pago"].sum() 
            total_saldo_pagamentos = total_valor_pago_credito + total_valor_pago_debito + total_valor_pago_deposito + total_valor_pago_dinheiro
            
            with st.container(border=True):
                st.markdown(f"### Balanço dos Pagamentos - ({start_date} - {end_date})")
                st.write(f"**Maquininha Pag Seguro Micas Virtual (Valor Total Pago com Taxas):** R$ {total_valor_pago_credito + total_valor_pago_debito + total_valor_taxa_maquina:.2f}")
                st.write(f"**Maquininha Pag Seguro Micas Virtual (Desconto das Taxas):** R$ {total_valor_taxa_maquina:.2f}")
                st.write(f"**Maquininha Pag Seguro Micas Virtual (Valor Saldo Total sem Taxas):** R$ {total_valor_pago_credito + total_valor_pago_debito:.2f}")
                st.write(f"**Depósito Micas Virtual (Total):** R$ {total_valor_pago_deposito:.2f}")
                st.write(f"**Dinheiro (Total):** R$ {total_valor_pago_dinheiro:.2f}")
                st.write(f"**Saldo Total: R$ {total_saldo_pagamentos:.2f}**")
            
                # Create a pie chart
                pie_data = {
                    "Forma de Pagamento": ["Crédito", "Débito", "Depósito", "Dinheiro"],
                    "Total Valor": [total_valor_pago_credito, total_valor_pago_debito, total_valor_pago_deposito, total_valor_pago_dinheiro]
                }
                pie_df = pd.DataFrame(pie_data)
                fig = px.pie(pie_df, values='Total Valor', names='Forma de Pagamento', title='Distribuição dos Pagamentos')
                st.plotly_chart(fig)

                st.write(f"**Crédito (Saldo Total sem Taxas):** R$ {total_valor_pago_credito:.2f}")
                st.write(f"**Débito (Saldo Total sem Taxas):** R$ {total_valor_pago_debito:.2f}")
                st.write(f"**Depósito (Total):** R$ {total_valor_pago_deposito:.2f}")
                st.write(f"**Dinheiro (Total):** R$ {total_valor_pago_dinheiro:.2f}")

        if evento_selecionado == "Todos":
            opcoes_registros = st.selectbox("Selecione filtros de Caixa", ["Entradas e Saídas", "Entradas", "Saídas"])
        
            df_caixa = carregar_dados_caixa()
            if opcoes_registros == "Entradas":
                df_caixa = df_caixa[df_caixa["Operação"] == "Entrada"]
            elif opcoes_registros == "Saídas":
                df_caixa = df_caixa[df_caixa["Operação"] == "Saída"]
            df_retiradas = df_caixa.copy()
            df_entradas = df_caixa.copy()

            df_entradas = df_entradas[df_entradas["Operação"]=="Entrada"]
            df_entradas["Data"] = pd.to_datetime(df_entradas["Data"], errors="coerce")
            df_entradas = df_entradas.dropna(subset=["Data"])
            df_entradas = df_entradas[(df_entradas["Data"] >= pd.to_datetime(start_date)) & (df_entradas["Data"] <= pd.to_datetime(end_date))]
            
            total_entradas = 0
            if not df_entradas.empty:
                with st.container(border=True):
                    st.markdown(f"### Entradas de Caixa (Avulsos Sem Pagamentos) - ({start_date} - {end_date})")
                    st.dataframe(df_entradas)
                    st.write(f"**Número de Entradas:** {len(df_entradas.index)}")
                    total_entradas = df_entradas["Valor"].sum()
                    st.write(f"**Entradas (Total):** R$ {total_entradas:.2f}")
            else:
                st.warning("Nenhuma entrada encontrada para o período selecionado.")

            df_retiradas = df_retiradas[df_retiradas["Operação"]=="Saída"]
            df_retiradas["Data"] = pd.to_datetime(df_retiradas["Data"], errors="coerce")
            df_retiradas = df_retiradas.dropna(subset=["Data"])
            df_retiradas = df_retiradas[(df_retiradas["Data"] >= pd.to_datetime(start_date)) & (df_retiradas["Data"] <= pd.to_datetime(end_date))]
            
            total_retiradas = 0
            if not df_retiradas.empty:
                with st.container(border=True):
                    st.markdown(f"### Saídas/Retiradas de Caixa - ({start_date} - {end_date})")
                    st.dataframe(df_retiradas)
                    st.write(f"**Número de Saídas:** {len(df_retiradas.index)}")
                    total_retiradas = df_retiradas["Valor"].sum()
                    st.write(f"**Saídas (Total):** R$ {total_retiradas:.2f}")
            else:
                st.warning("Nenhuma saída encontrada para o período selecionado.")

            with st.container(border=True):
                st.markdown(f"### Caixa Final - ({start_date} - {end_date})")
                st.write(f"**Dinheiro Recebido Pagamentos (Total):** R$ {total_saldo_pagamentos:.2f}")
                st.write(f"**Entradas Avulsas (Total):** R$ {total_entradas:.2f}")
                st.write(f"**Saídas/Retiradas (Total):** R$ {total_retiradas:.2f}")    
                st.write(f"**Caixa do Período (Final): R$ {(total_saldo_pagamentos+total_entradas) - total_retiradas:.2f}**")

        # Botão para exportar para PDF
        if st.button("Exportar para PDF"): 
            if evento_selecionado == "Todos":
                base_path, pdf_path = exportar_pagamentos_para_pdf(start_date, end_date, total_valor_credito, total_valor_pago_credito, total_valor_debito, total_valor_pago_debito, total_valor_deposito, total_valor_dinheiro, total_retiradas, df_retiradas, total_entradas, df_entradas)
                st.success(f"Arquivo PDF salvo como {base_path+pdf_path}")
                st.download_button(
                    label="Baixar PDF",
                    data=open(base_path+pdf_path, "rb").read(),
                    file_name=pdf_path,
                    mime="application/pdf"
                )
            else:
                st.warning("Exportação para PDF disponível apenas para 'Todos'.")             
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")