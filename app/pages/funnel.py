import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from app.utils.helpers import get_db_connection

def funnel_report():
    st.header("Relatório de Eventos")

    conn = get_db_connection()
    
    # Load data from the database
    eventos = pd.read_sql_query("SELECT * FROM eventos", conn)

    # Update start_date and end_date to use "Data" from eventos
    fallback_date = datetime.date.today()
    min_date = pd.to_datetime(eventos["Data"], errors="coerce").min()
    max_date = pd.to_datetime(eventos["Data"], errors="coerce").max()

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
    eventos = pd.read_sql_query(f"""SELECT * FROM eventos WHERE "Data" BETWEEN '{start_date}' AND '{end_date}'""", conn)
    participantes = pd.read_sql_query( f"""SELECT * FROM participantes WHERE "Data" BETWEEN '{start_date}' AND '{end_date}'""", conn)
    orcamentos_meninas = pd.read_sql_query(f"""SELECT * FROM orcamentos_meninas WHERE "Data" BETWEEN '{start_date}' AND '{end_date}'""", conn)
    orcamentos_meninos = pd.read_sql_query(f"""SELECT * FROM orcamentos_meninos WHERE "Data" BETWEEN '{start_date}' AND '{end_date}'""", conn)
    orcamentos = pd.DataFrame()

    if not orcamentos_meninas.empty or not orcamentos_meninos.empty:
        # Concatenate only non-empty DataFrames
        orcamentos = pd.concat(
            [df for df in [orcamentos_meninas, orcamentos_meninos] if not df.empty],
            ignore_index=True
        )

    if not participantes.empty:
        participantes = participantes.merge(
            eventos[["id", "Nome", "Data do Evento"]],
            left_on="Evento_id",
            right_on="id",
            how="left"
        )
        participantes = participantes.drop(columns=["id_y", "Evento_id"])
        participantes.rename(columns={"Nome_x": "Nome do Participante", "Nome_y": "Nome do Cliente", "id_x": "id", "Data_y": "Data do Evento", "Data_x": "Data de Criação do Participante"}, inplace=True)

        # Adjust column order
        
        if "Data de Criação do Participante" in participantes.columns:  # Ensure 'Data' exists before popping
            sec_column = participantes.pop("Data de Criação do Participante")
            participantes.insert(1, "Data de Criação do Participante", sec_column)
        if "Data do Evento" in participantes.columns:  # Ensure 'Data' exists before popping
            third_column = participantes.pop("Data do Evento")
            participantes.insert(2, "Data do Evento", third_column) 
        if "Nome do Cliente" in participantes.columns:
            fir_column = participantes.pop("Nome do Cliente")         
            participantes.insert(3, "Nome do Cliente", fir_column)
   

    # Merge orcamentos values into participantes
    if not orcamentos.empty:
        participantes = participantes.merge(
            orcamentos[["Participante_id", "Valor Pago", "Valor Total", "Tipo de Pagamento", "Status"]],
            left_on="id",
            right_on="Participante_id",
            how="left"
        )
        participantes = participantes.drop(columns=["Participante_id"], errors="ignore")
        participantes.rename(columns={"Status_x": "Status Participante", "Status_y": "Status Orçamento"}, inplace=True)

        # Fill null values with "Orçamento não existente"
        participantes[["Valor Pago", "Valor Total", "Tipo de Pagamento"]] = participantes[
            ["Valor Pago", "Valor Total", "Tipo de Pagamento"]
        ].fillna("Não existente")

        # Ensure consistent data types for 'Tipo de Pagamento'
        participantes["Tipo de Pagamento"] = participantes["Tipo de Pagamento"].astype(str)

        # Move "Valor Pago", "Valor Total", and "Tipo de Pagamento" after "Status"
        for column in ["Valor Pago", "Valor Total", "Tipo de Pagamento"]:
            col_data = participantes.pop(column)
            status_index = participantes.columns.get_loc("Status Participante")
            participantes.insert(status_index + 1, column, col_data)
    else:
        # Handle case where orcamentos is empty
        participantes["Valor Pago"] = "Não Existente"
        participantes["Valor Total"] = "Não Existente"
        participantes["Tipo de Pagamento"] = "Não Existente"
        participantes["Status Orçamento"] = "Não Existente"

    # Ensure 'Status Orçamento' column exists or fallback to 'Status Participante'
    if 'Status Orçamento' not in participantes.columns:
        participantes['Status Orçamento'] = "Não Existente"

    if 'Status Participante' not in participantes.columns: 
        participantes.rename(columns={"Status": "Status Participante"}, inplace=True)

    if not participantes.empty:
        last_column = participantes.pop("Status Participante")
        participantes.insert(len(participantes.columns)-1, "Status Participante", last_column)

        status_options_participantes = participantes["Status Participante"].unique().tolist()
        status_options_orcamentos = participantes["Status Orçamento"].unique().tolist()
        status_filter_p = st.selectbox("Filtrar por Status Participante", ["Todos"] + status_options_participantes)
        status_filter_o = st.selectbox("Filtrar por Status Orçamento", ["Todos","Todos (exceto Pagamento Completo)"] + status_options_orcamentos)

        if (status_filter_p != "Todos"):
            participantes = participantes[participantes["Status Participante"] == status_filter_p]
        if (status_filter_o != "Todos") and (status_filter_o != "Todos (exceto Pagamento Completo)"):
            participantes = participantes[participantes["Status Orçamento"] == status_filter_o]    

        st.dataframe(participantes)

        total_novo_cadastro = len(participantes[participantes["Status Participante"]=="Novo Cadastro"])
        total_cadastro_modificado = len(participantes[participantes["Status Participante"]=="Cadastro Modificado"])
        total_cadastro_orcamento_criado = len(participantes[participantes["Status Orçamento"]=="Novo Orçamento"])
        total_cadastro_orcamento_deletado = len(participantes[participantes["Status Orçamento"]=="Não Existente"])
        total_cadastro_orcamento_atualizado = len(participantes[participantes["Status Orçamento"]=="Orçamento Atualizado"])
        total_cadastro_orcamento_completo = len(participantes[participantes["Status Orçamento"]=="Pagamento Completo"])
        total_cadastro_orcamento_nao_completo = len(participantes) - total_cadastro_orcamento_completo
        if status_filter_p == "Todos" and status_filter_o == "Todos":
            with st.container(border=True):
                st.markdown("### Status dos Participantes dos Eventos")
                st.write(f"**Total Novo Cadastro:** {total_novo_cadastro}")
                st.write(f"**Total Cadastro Modificado:** {total_cadastro_modificado}")
                st.write("")
                st.markdown("### Status dos Orçamentos dos Participantes dos Eventos")
                st.write(f"**Total Orçamento Não Existente:** {total_cadastro_orcamento_deletado}")
                st.write(f"**Total Novo Orçamento:** {total_cadastro_orcamento_criado}")
                st.write(f"**Total Orçamento Atualizado:** {total_cadastro_orcamento_atualizado}")
                st.write(f"**Total Pagamento Completo:** {total_cadastro_orcamento_completo}")
                st.write("")
                status_counts = {
                    "Orçamento Não Existente": total_cadastro_orcamento_deletado,
                    "Novo Orçamento": total_cadastro_orcamento_criado,
                    "Orçamento Atualizado": total_cadastro_orcamento_atualizado,
                    "Pagamento Completo": total_cadastro_orcamento_completo
                }
                status_df_1 = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
                fig_1 = px.pie(status_df_1, values="Count", names="Status", title="Distribuição de Status dos Orçamentos")
                st.plotly_chart(fig_1)

                st.markdown("### Status Gerais")
                st.write(f"**Total Completo:** {total_cadastro_orcamento_completo}")
                st.write(f"**Total Não Completo:** {total_cadastro_orcamento_nao_completo}")
                st.write(f"**Total:** {total_cadastro_orcamento_completo+total_cadastro_orcamento_nao_completo}")
                status_counts = {
                    "Total Completo": total_cadastro_orcamento_nao_completo,
                    "Total Não Completo": total_cadastro_orcamento_completo
                }
                status_df_2 = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
                fig_2 = px.pie(status_df_2, values="Count", names="Status", title="Distribuição de Status dos Pagamentos")
                st.plotly_chart(fig_2)
        elif status_filter_p == "Todos" and status_filter_o == "Todos (exceto Pagamento Completo)":
            with st.container(border=True):
                st.markdown("### Status dos Participantes dos Eventos")
                st.write(f"**Total Novo Cadastro:** {total_novo_cadastro}")
                st.write(f"**Total Cadastro Modificado:** {total_cadastro_modificado}")
                st.write("")
                st.markdown("### Status dos Orçamentos dos Participantes dos Eventos")
                st.write(f"**Total Orçamento Não Existente:** {total_cadastro_orcamento_deletado}")
                st.write(f"**Total Novo Orçamento:** {total_cadastro_orcamento_criado}")
                st.write(f"**Total Orçamento Atualizado:** {total_cadastro_orcamento_atualizado}")
                st.write("")
                st.write(f"**Total Não Completo:** {total_cadastro_orcamento_nao_completo}")

                status_counts = {
                    "Novo Orçamento": total_cadastro_orcamento_criado,
                    "Orçamento Não Existente": total_cadastro_orcamento_deletado,
                    "Orçamento Atualizado": total_cadastro_orcamento_atualizado
                }
                status_df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
                fig = px.pie(status_df, values="Count", names="Status", title="Distribuição de Status dos Eventos")
                st.plotly_chart(fig)
        else:
            with st.container(border=True):
                st.markdown("### Status dos Eventos")
                if status_filter_p == "Novo Cadastro":
                    st.write(f"**Total Novo Cadastro:** {total_novo_cadastro}")
                elif status_filter_p == "Cadastro Modificado":
                    st.write(f"**Total Cadastro Modificado:** {total_cadastro_modificado}")
                elif status_filter_o == "Novo Orçamento":
                    st.write(f"**Total Novo Orçamento:** {total_cadastro_orcamento_criado}")
                elif status_filter_o == "Não Existente":
                    st.write(f"**Total Não Existente:** {total_cadastro_orcamento_deletado}")
                elif status_filter_o == "Orçamento Atualizado":
                    st.write(f"**Total Orçamento Atualizado:** {total_cadastro_orcamento_atualizado}")
                elif status_filter_o == "Pagamento Completo":
                    st.write(f"**Total Pagamento Completo:** {total_cadastro_orcamento_completo}")
    else:   
        st.warning("Nenhum cliente encontrado.")
