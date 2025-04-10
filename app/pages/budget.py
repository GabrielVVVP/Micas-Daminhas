import streamlit as st
import pandas as pd
import datetime as dt
import time
from app.utils.helpers import get_db_connection
from app.utils.orcamentos import salvar_dados_orcamentos, atualizar_dados_orcamentos, deletar_dados_orcamentos
from app.utils.participantes import atualizar_status_participante
from app.utils.caixa import salvar_dados_caixa, atualizar_dados_caixa_id, deletar_dados_caixa_id

def budget():
    st.header("Orçamento")	

    conn = get_db_connection()
    if "show_novo_orcamento_form" not in st.session_state:
            st.session_state.show_novo_orcamento_form = False

    orcamento_existente = pd.DataFrame()
    fallback_date = dt.date.today()
    clientes = pd.read_sql_query("SELECT * FROM eventos", conn)
    min_date = pd.to_datetime(clientes["Data"], errors="coerce").min()
    max_date = pd.to_datetime(clientes["Data"], errors="coerce").max()
    start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
    end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)
    filtered_clientes = clientes[
        (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
        (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
    ]
    cliente_selecionado = st.selectbox("Selecione o Cliente", filtered_clientes["Nome"] if not filtered_clientes.empty else [])
    if clientes.empty:
        st.warning("Nenhum cliente encontrado.")
    elif filtered_clientes.empty:
        st.warning("Nenhum cliente encontrado para o intervalo de datas selecionado.")    
    if cliente_selecionado:
        evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]
        participantes = pd.read_sql_query(f"SELECT id, Nome, Tipo, [Responsável Financeiro] FROM participantes WHERE Evento_id = {evento_id}", conn)
        participante_selecionado = st.selectbox("Selecione o Participante", participantes["Nome"])
        if participantes.empty:
            st.warning("Nenhum participante encontrado para o cliente selecionado.")
        else:
            participante_id = participantes[participantes["Nome"] == participante_selecionado]["id"].values[0]
            participante_tipo = participantes[participantes["Nome"] == participante_selecionado]["Tipo"].values[0]

            if participante_tipo == "Menina":
                orcamento_existente = pd.read_sql_query(
                f"SELECT * FROM orcamentos_meninas WHERE Evento_id = {evento_id} AND Participante_id = {participante_id}", conn
                )
            else:
                orcamento_existente = pd.read_sql_query(
                f"SELECT * FROM orcamentos_meninos WHERE Evento_id = {evento_id} AND Participante_id = {participante_id}", conn
                )

    if not orcamento_existente.empty:
        # Replace Evento_id with Nome from eventos
        eventos_dict = clientes.set_index("id")["Nome"].to_dict()
        orcamento_existente["Evento"] = orcamento_existente["Evento_id"].map(eventos_dict)

        # Replace Participante_id with Nome from participantes
        participantes_dict = participantes.set_index("id")["Nome"].to_dict()
        orcamento_existente["Participante"] = orcamento_existente["Participante_id"].map(participantes_dict)

        # Add Responsável Financeiro from participantes to orcamento_existente
        orcamento_existente["Responsável Financeiro"] = orcamento_existente["Participante_id"].map(participantes.set_index("id")["Responsável Financeiro"])

        # Drop the id column and reorder columns for display
        orcamento_original = orcamento_existente.copy()
        orcamento_existente = orcamento_existente.drop(columns=["id", "Evento_id", "Participante_id"])
        # Reorder columns to move Responsável Financeiro before Valor Total
        orcamento_existente = orcamento_existente[["Evento", "Participante", "Responsável Financeiro"] + [col for col in orcamento_existente.columns if col not in ["Evento", "Participante", "Responsável Financeiro"]]]

        # Ensure all columns are Arrow-compatible by converting floats to strings where necessary
        for column in orcamento_existente.columns:
            if orcamento_existente[column].dtype == 'float':
                orcamento_existente[column] = orcamento_existente[column].astype(str)

        # Replace NaN values with empty strings for compatibility
        orcamento_existente = orcamento_existente.fillna('')

        st.markdown("### Informações do Orçamento Existente")
        st.table(orcamento_existente.T)

        """print(orcamento_existente.dtypes)  # Check the data types of all columns
        print(orcamento_existente.head())  # Inspect the first few rows of the DataFrame
        for column in orcamento_existente.columns:
            print(f"Column: {column}, Unique Values: {orcamento_existente[column].unique()}")"""

        st.warning("Já existe um orçamento para este participante.")
        st.markdown("### Editar Orçamento Existente")
        opcao_orcamento_editar = st.selectbox("Selecione o tipo de Modificação", ["Editar Medidas", "Editar Orçamento"])	
        if opcao_orcamento_editar == "Editar Medidas":
            st.markdown("### Editar Medidas")
            with st.form(key='editar_medidas_form'):
                if participante_tipo == "Menina":
                    busto = st.number_input("Busto (cm)", min_value=0.0, value=float(orcamento_existente["Busto"].values[0]))
                    cintura = st.number_input("Cintura (cm)", min_value=0.0, value=float(orcamento_existente["Cintura"].values[0]))
                    ombro_cint = st.number_input("Ombro-Cintura (cm)", min_value=0.0, value=float(orcamento_existente["Ombro-Cintura"].values[0]))
                    cint_pe = st.number_input("Cintura-Pé (cm)", min_value=0.0, value=float(orcamento_existente["Cintura-Pé"].values[0]))
                    modelo = st.text_area("Modelo", value=orcamento_existente["Modelo"].values[0])
                    acessorios = st.text_area("Acessórios", value=orcamento_existente["Acessórios"].values[0])
                    observacao = st.text_area("Observação", value=orcamento_existente["Observação"].values[0])
                elif participante_tipo == "Menino":
                    ombro_punho = st.number_input("Ombro-Punho (cm)", min_value=0.0, value=float(orcamento_existente["Ombro-Punho"].values[0]))
                    bainha_calca = st.number_input("Bainha-Calça (cm)", min_value=0.0, value=float(orcamento_existente["Bainha-Calça"].values[0]))
                    modelo = st.text_area("Modelo", value=orcamento_existente["Modelo"].values[0])
                    acessorios = st.text_area("Acessórios", value=orcamento_existente["Acessórios"].values[0])
                    observacao = st.text_area("Observação", value=orcamento_existente["Observação"].values[0])
                col1, col2 = st.columns(2)
                with col1:
                    update_button = st.form_submit_button(label="Atualizar Medidas")
                with col2:
                    delete_button = st.form_submit_button(label="Deletar Orçamento")

                if update_button:
                    if participante_tipo == "Menina":
                        orcamento_atualizado = {
                            "Evento_id": evento_id,
                            "Participante_id": participante_id,
                            "Busto": busto,
                            "Cintura": cintura,
                            "Ombro-Cintura": ombro_cint,
                            "Cintura-Pé": cint_pe,
                            "Modelo": modelo,
                            "Acessórios": acessorios,
                            "Observação": observacao,
                            "Status": "Medidas Atualizadas"
                        }
                    elif participante_tipo == "Menino":  
                        orcamento_atualizado = {
                            "Evento_id": evento_id,
                            "Participante_id": participante_id,
                            "Ombro-Punho": ombro_punho,
                            "Bainha-Calça": bainha_calca,
                            "Modelo": modelo,
                            "Acessórios": acessorios,
                            "Observação": observacao,
                            "Status": "Medidas Atualizadas"
                        } 
                    df_orcamento_atualizado = pd.DataFrame([orcamento_atualizado])
                    atualizar_dados_orcamentos(df_orcamento_atualizado,opcao_orcamento_editar)
                    atualizar_status_participante(participante_id, "Medidas Atualizadas")
                    st.success("Orçamento atualizado com sucesso!")
                    time.sleep(2)
                    st.rerun()

                if delete_button:
                    deletar_dados_orcamentos(orcamento_original['id'].values[0],participante_tipo)
                    atualizar_status_participante(participante_id, "Orçamento Deletado")
                    st.success("Orçamento deletado com sucesso!")
                    time.sleep(2)
                    st.rerun()
        else:
            st.markdown("### Editar Orçamento")
            with st.form(key='editar_orcamento_form'):
                valor_total = st.number_input("Valor Total do Orçamento", min_value=0.0, value=float(orcamento_existente["Valor Total"].values[0]))
                valor_pago = st.number_input("Valor Pago", min_value=0.0, value=float(orcamento_existente["Valor Pago"].values[0]))
                if valor_pago > valor_total:
                    st.error("O Valor Pago não pode ser maior que o Valor Total.")
                else:
                    tipo_pagamento = st.selectbox(
                        "Tipo de Pagamento", 
                        ["Dinheiro", "Depósito", "Crédito", "Débito"], 
                        index=["Dinheiro", "Depósito", "Crédito", "Débito"].index(orcamento_existente["Tipo de Pagamento"].values[0])
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button(label="Atualizar Orçamento")
                    with col2:
                        delete_button = st.form_submit_button(label="Deletar Orçamento")

                    if update_button and valor_pago <= valor_total:
                        if valor_pago == valor_total:
                            status_pagamento = "Pagamento Completo"
                        else: 
                            status_pagamento = "Orçamento Atualizado"    
                        orcamento_atualizado = {
                                "Evento_id": evento_id,
                                "Participante_id": participante_id,
                                "Valor Total": valor_total,
                                "Valor Pago": valor_pago,
                                "Tipo de Pagamento": tipo_pagamento,
                                "Status": status_pagamento
                        }
                        df_orcamento_atualizado = pd.DataFrame([orcamento_atualizado])
                        atualizar_dados_orcamentos(df_orcamento_atualizado,opcao_orcamento_editar)
                        atualizar_status_participante(participante_id, status_pagamento)
                        if tipo_pagamento == "Dinheiro":
                            caixa_registro = {
                                    "Participante_id": participante_id,
                                    "Data": pd.to_datetime("now").date(),
                                    "Observação": "Pagamento Evento",
                                    "Valor": valor_pago,
                                    "Operação": "Entrada"
                            }
                            df_caixa_registro = pd.DataFrame([caixa_registro])
                            message = atualizar_dados_caixa_id(df_caixa_registro)
                            if message != None:
                                salvar_dados_caixa(df_caixa_registro)
                        if (orcamento_existente["Tipo de Pagamento"].values[0] == "Dinheiro") and (tipo_pagamento != "Dinheiro"): 
                            deletar_dados_caixa_id(int(participante_id))
                        st.success("Orçamento atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()

                    if delete_button:
                        deletar_dados_orcamentos(orcamento_original['id'].values[0],participante_tipo)
                        atualizar_status_participante(participante_id, "Orçamento Deletado")
                        if tipo_pagamento == "Dinheiro":
                            deletar_dados_caixa_id(int(participante_id))
                        st.success("Orçamento deletado com sucesso!")
                        time.sleep(2)
                        st.rerun()
                            
    elif cliente_selecionado and not participantes.empty:
        st.info("Nenhum orçamento encontrado para este participante.")
        if st.button("Novo Orçamento"):
            st.session_state.show_novo_orcamento_form = not st.session_state.show_novo_orcamento_form
        if st.session_state.show_novo_orcamento_form:
            st.markdown("### Novo Orçamento")
            with st.form(key='novo_cadastro_form'):
                if clientes[clientes["Nome"] == cliente_selecionado]["Tipo_Evento"].values[0] == "Escola":
                    st.markdown(f"### Novo Orçamento Formatura")
                else:
                    st.markdown(f"### Novo Orçamento Casamento")   
                
                if participante_tipo == "Menina":
                    busto = st.number_input("Busto (cm)", min_value=0.0)
                    cintura = st.number_input("Cintura (cm)", min_value=0.0)
                    ombro_cint = st.number_input("Ombro-Cintura (cm)", min_value=0.0)
                    cint_pe = st.number_input("Cintura-Pé (cm)", min_value=0.0)
                    modelo = st.text_area("Modelo")
                    acessorios = st.text_area("Acessórios")
                    observacao = st.text_area("Observação")
                    valor_total = st.number_input("Valor Total do Orçamento", min_value=0.0)
                    
                    # Add the submit button
                    submit_button = st.form_submit_button(label="Salvar Registro")

                    if submit_button:
                        if all([busto > 0, cintura > 0, ombro_cint > 0, cint_pe > 0, modelo, acessorios, valor_total > 0]):
                            novo_registro = {
                                "Evento_id": evento_id,
                                "Participante_id": participante_id,
                                "Data": pd.to_datetime("now").date(),
                                "Busto": busto,
                                "Cintura": cintura,
                                "Ombro-Cintura": ombro_cint,
                                "Cintura-Pé": cint_pe,
                                "Modelo": modelo,
                                "Acessórios": acessorios,
                                "Observação": observacao if observacao != "" else "Sem Observação",
                                "Valor Total": valor_total,
                                "Desconto": 0,
                                "Valor Pago": 0,
                                "Tipo de Pagamento": "Não definido",
                                "Contrato Retirada": "Não emitido",
                                "Status Contrato Retirada": "Não emitido",
                                "Contrato Devolução": "Não emitido",
                                "Status Contrato Devolução": "Não emitido",
                                "Status": "Novo Orçamento"
                            }
                            df_novo_registro = pd.DataFrame([novo_registro])
                            salvar_dados_orcamentos(df_novo_registro, participante_tipo)
                            atualizar_status_participante(participante_id, "Novo Orçamento")
                            """if tipo_pagamento == "Dinheiro":
                                caixa_registro = {
                                    "Participante_id": participante_id,
                                    "Data": pd.to_datetime("now").date(),
                                    "Observação": "Pagamento Evento",
                                    "Valor": valor_pago,
                                    "Operação": "Entrada"
                                }
                                df_caixa_registro = pd.DataFrame([caixa_registro])
                                salvar_dados_caixa(df_caixa_registro)"""
                            st.success("Orçamento salvo com sucesso!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Por favor, preencha todos os campos obrigatórios.")
                
                elif participante_tipo == "Menino":
                    ombro_punho = st.number_input("Ombro-Punho (cm)", min_value=0.0)
                    bainha_calca = st.number_input("Bainha-Calça (cm)", min_value=0.0)
                    modelo = st.text_input("Modelo")
                    acessorios = st.text_area("Acessórios")
                    observacao = st.text_area("Observação")
                    valor_total = st.number_input("Valor Total do Orçamento", min_value=0.0)
                    
                    # Add the submit button
                    submit_button = st.form_submit_button(label="Salvar Registro")

                    if submit_button:
                        if all([ombro_punho > 0, bainha_calca > 0, modelo, acessorios, valor_total > 0]):
                            novo_registro = {
                                "Evento_id": evento_id,
                                "Participante_id": participante_id,
                                "Data": pd.to_datetime("now").date(),
                                "Ombro-Punho": ombro_punho,
                                "Bainha-Calça": bainha_calca,
                                "Modelo": modelo,
                                "Acessórios": acessorios,
                                "Observação": observacao if observacao != "" else "Sem Observação",
                                "Valor Total": valor_total,
                                "Desconto": 0,
                                "Valor Pago": 0,
                                "Tipo de Pagamento": "Não definido",
                                "Contrato Retirada": "Não emitido",
                                "Status Contrato Retirada": "Não emitido",
                                "Contrato Devolução": "Não emitido",
                                "Status Contrato Devolução": "Não emitido",
                                "Status": "Novo Orçamento"
                            }
                            df_novo_registro = pd.DataFrame([novo_registro])
                            salvar_dados_orcamentos(df_novo_registro, participante_tipo)
                            atualizar_status_participante(participante_id, "Novo Orçamento")
                            """if tipo_pagamento == "Dinheiro":
                                caixa_registro = {
                                    "Participante_id": participante_id,
                                    "Data": pd.to_datetime("now").date(),
                                    "Observação": "Pagamento Evento",
                                    "Valor": valor_pago,
                                    "Operação": "Entrada"
                                }
                                df_caixa_registro = pd.DataFrame([caixa_registro])
                                salvar_dados_caixa(df_caixa_registro)"""
                            st.success("Orçamento salvo com sucesso!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Por favor, preencha todos os campos obrigatórios.")





