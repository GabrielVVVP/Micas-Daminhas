import streamlit as st
import pandas as pd
import datetime as dt
import time
from app.utils.helpers import get_db_connection
from app.utils.orcamentos import get_orcamentos,salvar_dados_orcamentos, atualizar_dados_orcamentos, deletar_dados_orcamentos
from app.utils.participantes import get_participantes_event, atualizar_status_participante
from app.utils.eventos import update_client_params
from app.utils.pdf import exportar_producao_para_pdf

def budget():
    st.header("Medidas e Orçamentos")	

    conn = get_db_connection()
    if "show_novo_orcamento_form" not in st.session_state:
            st.session_state.show_novo_orcamento_form = False

    orcamento_existente = pd.DataFrame()
    clientes = pd.read_sql_query("SELECT * FROM eventos", conn)

    # Update start_date and end_date to use "Data" from eventos
    fallback_date = dt.date.today()
    min_date = pd.to_datetime(clientes["Data"], errors="coerce").min()
    max_date = pd.to_datetime(clientes["Data"], errors="coerce").max()

    # Replace buttons with a select box for date range selection
    date_option = st.selectbox("Selecione o período", ["Dia", "Mês", "Ano", "Seletor de Datas"], index=1)

    if date_option == "Dia":
        start_date = dt.date.today()
        end_date = dt.date.today()
    elif date_option == "Mês":
        start_date = dt.date.today().replace(day=1)
        end_date = (dt.date.today().replace(day=1) + dt.timedelta(days=31)).replace(day=1) - dt.timedelta(days=1)
    elif date_option == "Ano":
        start_date = dt.date.today().replace(month=1, day=1)
        end_date = dt.date.today().replace(month=12, day=31)
    elif date_option == "Todos":
        start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
        end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)  
    elif date_option == "Seletor de Datas":
        start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
        end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)
        
    filtered_clientes = clientes[
        (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
        (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
    ]
    cliente_selecionado = st.selectbox("Selecione o Cliente", filtered_clientes["Nome"] if not filtered_clientes.empty else [])
    modo_selecionado = st.selectbox("Selecione o modo", ["Adicionar/Modificar Orçamento", "Produção de Vestidos"])
    if clientes.empty:
        st.warning("Nenhum cliente encontrado.")
    elif filtered_clientes.empty:
        st.warning("Nenhum cliente encontrado para o intervalo de datas selecionado.")  
    if modo_selecionado ==  "Adicionar/Modificar Orçamento":      
        if cliente_selecionado:
            evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]
            #participantes = pd.read_sql_query(f"SELECT id, Nome, Tipo FROM participantes WHERE Evento_id = {evento_id}", conn)
            participantes = get_participantes_event(evento_id)
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

            # Drop the id column and reorder columns for display
            orcamento_original = orcamento_existente.copy()
            orcamento_existente = orcamento_existente.drop(columns=["id", "Evento_id", "Participante_id"])
            orcamento_existente = orcamento_existente[["Evento", "Participante"] + [col for col in orcamento_existente.columns if col not in ["Evento", "Participante"]]]

            # Ensure all columns are Arrow-compatible by converting floats to strings where necessary
            for column in orcamento_existente.columns:
                if orcamento_existente[column].dtype == 'float':
                    orcamento_existente[column] = orcamento_existente[column].astype(str)

            # Replace NaN values with empty strings for compatibility
            orcamento_existente = orcamento_existente.fillna('')

            st.markdown("### Informações do Orçamento Existente")
            st.table(orcamento_existente.T)

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
                        data_retirada = st.date_input("Data da Retirada", value=orcamento_existente["Data Retirada"].values[0])
                        estado_retirada = st.text_input("Estado da Retirada", value=orcamento_existente["Estado Retirada"].values[0])
                        data_devolucao = st.date_input("Data da Devolução", value=orcamento_existente["Data Devolução"].values[0])
                        estado_devolucao = st.text_input("Estado da Devolução", value=orcamento_existente["Estado Devolução"].values[0])
                    elif participante_tipo == "Menino":
                        ombro_punho = st.number_input("Ombro-Punho (cm)", min_value=0.0, value=float(orcamento_existente["Ombro-Punho"].values[0]))
                        bainha_calca = st.number_input("Bainha-Calça (cm)", min_value=0.0, value=float(orcamento_existente["Bainha-Calça"].values[0]))
                        modelo = st.text_area("Modelo", value=orcamento_existente["Modelo"].values[0])
                        acessorios = st.text_area("Acessórios", value=orcamento_existente["Acessórios"].values[0])
                        observacao = st.text_area("Observação", value=orcamento_existente["Observação"].values[0])
                        data_retirada = st.date_input("Data da Retirada", value=orcamento_existente["Data Retirada"].values[0])
                        estado_retirada = st.text_input("Estado da Retirada", value=orcamento_existente["Estado Retirada"].values[0])
                        data_devolucao = st.date_input("Data da Devolução", value=orcamento_existente["Data Devolução"].values[0])
                        estado_devolucao = st.text_input("Estado da Devolução", value=orcamento_existente["Estado Devolução"].values[0])
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
                                "Data Retirada": data_retirada,
                                "Estado Retirada": estado_retirada,
                                "Data Devolução": data_devolucao,
                                "Estado Devolução": estado_devolucao,
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
                                "Data Retirada": data_retirada,
                                "Estado Retirada": estado_retirada,
                                "Data Devolução": data_devolucao,
                                "Estado Devolução": estado_devolucao,
                                "Status": "Medidas Atualizadas"
                            } 
                        df_orcamento_atualizado = pd.DataFrame([orcamento_atualizado])
                        atualizar_dados_orcamentos(df_orcamento_atualizado,opcao_orcamento_editar)
                        atualizar_status_participante(participante_id, "Medidas Atualizadas")
                        st.success("Orçamento atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()

                    if delete_button:
                        deletar_dados_orcamentos(int(orcamento_original['id'].values[0]),participante_tipo)
                        atualizar_status_participante(participante_id, "Orçamento Deletado")
                        st.success("Orçamento deletado com sucesso!")
                        time.sleep(2)
                        st.rerun()
            else:
                st.markdown("### Editar Orçamento")
                with st.form(key='editar_orcamento_form'):
                    valor_total = st.number_input("Valor Total do Orçamento", min_value=0.0, value=float(orcamento_existente["Valor Total"].values[0]))
                    discount = st.number_input("Desconto (R$)", min_value=0.0, max_value=float(orcamento_existente["Valor Total"].values[0]), value=float(orcamento_existente["Taxa de Desconto"].values[0]))
                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button(label="Atualizar Orçamento")
                    with col2:
                        delete_button = st.form_submit_button(label="Deletar Orçamento")

                    if update_button: 
                        status_pagamento = "Orçamento Atualizado"    
                        orcamento_atualizado = {
                                "Evento_id": evento_id,
                                "Participante_id": participante_id,
                                "Valor Total": valor_total,
                                "Taxa de Desconto": discount,
                                "Valor com Desconto": valor_total - discount,
                                "Status": status_pagamento
                        }
                        df_orcamento_atualizado = pd.DataFrame([orcamento_atualizado])
                        atualizar_dados_orcamentos(df_orcamento_atualizado,opcao_orcamento_editar)
                        atualizar_status_participante(participante_id, status_pagamento)
                        update_client_params(event_id=int(evento_id),params={"Status": "Orçamento Atualizado"})
                        st.success("Orçamento atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()

                    if delete_button:
                        deletar_dados_orcamentos(int(orcamento_original['id'].values[0]),participante_tipo)
                        atualizar_status_participante(participante_id, "Orçamento Deletado")
                        st.success("Orçamento deletado com sucesso!")
                        time.sleep(2)
                        st.rerun()
                                
        elif cliente_selecionado and not participantes.empty:
            st.info("Nenhum orçamento encontrado para este participante.")
            st.markdown("### Novo Orçamento")
            with st.form(key='novo_cadastro_form'):
                if clientes[clientes["Nome"] == cliente_selecionado]["Tipo Evento"].values[0] == "Escola":
                    st.markdown(f"### Novo Orçamento Formatura")
                else:
                    st.markdown(f"### Novo Orçamento Casamento")   
                
                if participante_tipo == "Menina":
                    busto = st.number_input("Busto (cm)", min_value=0.0)
                    cintura = st.number_input("Cintura (cm)", min_value=0.0)
                    ombro_cint = st.number_input("Ombro-Cintura (cm)", min_value=0.0)
                    cint_pe = st.number_input("Cintura-Pé (cm)", min_value=0.0)
                    modelo = st.text_area("Modelo", value="Vestido")
                    acessorios = st.text_area("Acessórios", value="Nenhum")
                    observacao = st.text_area("Observação", value="Nenhuma")
                    data_retirada = st.date_input("Data da Retirada")
                    estado_retirada = st.text_input("Estado da Retirada", value="Perfeito Estado")
                    data_devolucao = st.date_input("Data da Devolução")
                    estado_devolucao = st.text_input("Estado da Devolução", value="Perfeito Estado")
                    valor_total = st.number_input("Valor Total do Orçamento (R$)", min_value=0.0, value=0.0)
                    discount = st.number_input("Desconto (R$)", min_value=0.0)
                    
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
                                "Taxa de Desconto": discount,
                                "Valor com Desconto": valor_total - discount,
                                "Data Retirada": data_retirada,
                                "Estado Retirada": estado_retirada,
                                "Data Devolução": data_devolucao,
                                "Estado Devolução": estado_devolucao,
                                "Contrato Retirada": "Não emitido",
                                "Status Contrato Retirada": "Não emitido",
                                "Contrato Devolução": "Não emitido",
                                "Status Contrato Devolução": "Não emitido",
                                "Status": "Novo Orçamento"
                            }
                            df_novo_registro = pd.DataFrame([novo_registro])
                            salvar_dados_orcamentos(df_novo_registro, participante_tipo)
                            atualizar_status_participante(participante_id, "Novo Orçamento")
                            st.success("Orçamento salvo com sucesso!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Por favor, preencha todos os campos obrigatórios.")
                
                elif participante_tipo == "Menino":
                    ombro_punho = st.number_input("Ombro-Punho (cm)", min_value=0.0)
                    bainha_calca = st.number_input("Bainha-Calça (cm)", min_value=0.0)
                    modelo = st.text_input("Modelo", value="Terno")
                    acessorios = st.text_area("Acessórios", value="Nenhum")
                    observacao = st.text_area("Observação", value="Nenhuma")
                    data_retirada = st.date_input("Data Retirada")
                    estado_retirada = st.text_input("Estado Retirada", value="Perfeito Estado")
                    data_devolucao = st.date_input("Data Devolução")
                    estado_devolucao = st.text_input("Estado Devolução", value="Perfeito Estado")
                    valor_total = st.number_input("Valor Total do Orçamento", min_value=0.0)
                    discount = st.number_input("Desconto (R$)", min_value=0.0)
                    
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
                                "Taxa de Desconto": discount,
                                "Valor com Desconto": valor_total - discount,
                                "Data Retirada": data_retirada,
                                "Estado Retirada": estado_retirada,
                                "Data Devolução": data_devolucao,
                                "Estado Devolução": estado_devolucao,
                                "Contrato Retirada": "Não emitido",
                                "Status Contrato Retirada": "Não emitido",
                                "Contrato Devolução": "Não emitido",
                                "Status Contrato Devolução": "Não emitido",
                                "Status": "Novo Orçamento"
                            }
                            df_novo_registro = pd.DataFrame([novo_registro])
                            salvar_dados_orcamentos(df_novo_registro, participante_tipo)
                            atualizar_status_participante(participante_id, "Novo Orçamento")
                            st.success("Orçamento salvo com sucesso!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Por favor, preencha todos os campos obrigatórios.")
    else:
        cliente_dados = clientes[clientes["Nome"] == cliente_selecionado].iloc[0]
        evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]
        participantes = get_participantes_event(evento_id)
        if participantes.empty:
            st.warning("Nenhum participante encontrado para o cliente selecionado.")
            return
        participantes_dados_df = participantes.copy()
        participantes_dados_df = participantes_dados_df.drop(columns=["Evento_id", "id"], errors="ignore")
        participantes_dados_df.insert(2, "Nome do Cliente", cliente_dados["Nome"])
        st.write("#### Dados do Participantes")
        st.dataframe(participantes_dados_df)
        orcamento_meninas, orcamento_meninos = get_orcamentos(evento_id)

        if (not orcamento_meninas.empty) or (not orcamento_meninos.empty):
            st.markdown("### Dados do Orçamento das Meninas")
            if not orcamento_meninas.empty:
                participantes_dict = participantes.set_index("id")["Nome"].to_dict()
                orcamento_meninas["Participante_id"] = orcamento_meninas["Participante_id"].map(participantes_dict)
                orcamento_meninas = orcamento_meninas.drop(columns=["Evento_id", "id"], errors="ignore")
                orcamento_meninas.insert(1, "Nome do Cliente", cliente_dados["Nome"])
                orcamento_meninas.insert(2, "Nome do Participante", orcamento_meninas["Participante_id"])
                orcamento_meninas = orcamento_meninas.drop(columns=["Participante_id"], errors="ignore")
                st.write(orcamento_meninas)
            else:
                st.warning("Nenhum orçamento encontrado para as meninas.")
            st.markdown("### Dados do Orçamento dos Meninos")
            if not orcamento_meninos.empty:
                participantes_dict = participantes.set_index("id")["Nome"].to_dict()
                orcamento_meninos["Participante_id"] = orcamento_meninos["Participante_id"].map(participantes_dict)
                orcamento_meninos = orcamento_meninos.drop(columns=["Evento_id", "id"], errors="ignore")
                orcamento_meninos.insert(1, "Nome do Cliente", cliente_dados["Nome"])
                orcamento_meninos.insert(2, "Nome do Participante", orcamento_meninos["Participante_id"])
                orcamento_meninos = orcamento_meninos.drop(columns=["Participante_id"], errors="ignore")
                st.write(orcamento_meninos)
            else:
                st.warning("Nenhum orçamento encontrado para os meninos.")

            if st.button("Exportar Produção para PDF"): 
                base_path, pdf_path = exportar_producao_para_pdf(orcamento_meninas, orcamento_meninos, cliente_dados["Nome"])
                st.success(f"Arquivo PDF salvo como {base_path+pdf_path}")
                st.download_button(
                    label="Baixar PDF",
                    data=open(base_path+pdf_path, "rb").read(),
                    file_name=pdf_path,
                    mime="application/pdf"
                )                     





