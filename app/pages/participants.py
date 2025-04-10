import streamlit as st
import pandas as pd
import datetime as dt
import time
from app.utils.helpers import get_db_connection, is_valid_email, is_valid_cpf, is_valid_telefone
from app.utils.orcamentos import deletar_dados_orcamentos
from app.utils.participantes import salvar_dados_participantes, deletar_dados_participantes, atualizar_dados_participantes, atualizar_status_participante

def new_record():
    # Selecionar noiva da lista de eventos
    st.header("Cadastro Participantes")
    conn = get_db_connection()

    clientes = pd.read_sql_query("SELECT * FROM eventos", conn)
    # Update start_date and end_date to use "Data" from eventos
    min_date = pd.to_datetime(clientes["Data"], errors="coerce").min()
    max_date = pd.to_datetime(clientes["Data"], errors="coerce").max()

    # Fallback to today's date if min_date or max_date is NaT
    fallback_date = dt.date.today()
    start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
    end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)
    filtered_clientes = clientes[
        (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
        (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
    ]
    cliente_selecionado = st.selectbox("Selecione o Cliente", filtered_clientes["Nome"] if not filtered_clientes.empty else [])

    if cliente_selecionado:
        dados_cliente = clientes[clientes["Nome"] == cliente_selecionado]
        evento_id = dados_cliente["id"].values[0]
        participantes = pd.read_sql_query(f"SELECT * FROM participantes WHERE Evento_id = {evento_id}", conn)

        st.write(f"#### Evento: {dados_cliente['Tipo_Evento'].values[0]} de {cliente_selecionado}")
        dados_cliente_show = dados_cliente.copy()
        dados_cliente_show = dados_cliente_show.drop(columns=["id", "Evento_id"], errors="ignore")
        st.write(dados_cliente_show)

        st.markdown(f"### Participantes do Evento de {cliente_selecionado}")
        if not participantes.empty:
            participantes = participantes.astype(str)
            participantes_show = participantes.copy()
            participantes_show = participantes_show.drop(columns=["id", "Evento_id"], errors="ignore")
            st.write(participantes_show)  
            st.write(f"Total de Participantes: {len(participantes)}")
        else:
            st.warning("Nenhum participante encontrado para o evento selecionado.")
        
        options = st.selectbox("Tipo de Ação", ["Nenhum","Novo Participante", "Editar Participante"])	

        if options == "Novo Participante":
            st.markdown("### Novo Cadastro de Participante")
            
            with st.form(key='novo_participante_form'):
                nome = st.text_input("Nome")
                tipo = st.selectbox("Tipo de Participante", ["Menina", "Menino"])
                telefone = st.text_input("Telefone")
                email = st.text_input("Email")
                endereco = st.text_input("Endereço")
                cpf = st.text_input("CPF")
                
                submit_button = st.form_submit_button(label="Salvar Participante")

                if submit_button:
                    if not is_valid_email(email):
                        st.error("Email inválido. Certifique-se de que está no formato correto.")
                    elif not is_valid_cpf(cpf):
                        st.error("CPF inválido. Certifique-se de que contém 11 dígitos.")
                    elif not is_valid_telefone(telefone):
                        st.error("Telefone inválido. Certifique-se de que contém 11 dígitos.") 
                    else:       
                        novo_participante = {
                            "Evento_id": evento_id,
                            "Responsável Financeiro": "Não Definido",
                            "Data": pd.to_datetime("now").date(),
                            "Nome": nome,
                            "Tipo": tipo,
                            "Telefone": telefone,
                            "CPF": cpf,
                            "Email": email,
                            "Endereço": endereco,
                            "Status": "Novo Cadastro"
                        }
                        df_novo_participante = pd.DataFrame([novo_participante])
                        salvar_dados_participantes(df_novo_participante)
                        st.success("Participante atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()

        elif options == "Editar Participante":
            st.markdown("### Editar Participante")  
            if participantes.empty:  
                st.warning("Nenhum participante encontrado para o evento selecionado.")
            else:   
                for index, row in participantes.iterrows():
                    with st.form(key=f'participante_form_{index}'):
                        nome = st.text_input("Nome", value=row["Nome"], key=f'Nome_{index}')
                        tipo = st.selectbox("Tipo de Participante", options=["Menina", "Menino"], index=["Menina", "Menino"].index(row["Tipo"]), key=f'Tipo_{index}')
                        telefone = st.text_input("Telefone", value=row["Telefone"], key=f'Telefone_{index}')
                        email = st.text_input("Email", value=row["Email"], key=f'Email_{index}')
                        endereco = st.text_input("Endereço", value=row["Endereço"], key=f'Endereco_{index}')
                        cpf = st.text_input("CPF", value=row["CPF"], key=f'Cpf_{index}')
                        col1, col2 = st.columns(2)
                        with col1:
                            update_button = st.form_submit_button(label="Atualizar Participante")
                        with col2:
                            delete_button = st.form_submit_button(label="Deletar Participante")

                        if update_button:
                            if not is_valid_email(email):
                                st.error("Email inválido. Certifique-se de que está no formato correto.")
                            elif not is_valid_cpf(cpf):
                                st.error("CPF inválido. Certifique-se de que contém 11 dígitos.")
                            elif not is_valid_telefone(telefone):
                                st.error("Telefone inválido. Certifique-se de que contém 11 dígitos.") 
                            else:    
                                participante_atualizado = {
                                    "id": row["id"],
                                    "Evento_id": evento_id,
                                    "Responsável Financeiro": "Não Definido",	
                                    "Nome": nome,
                                    "Tipo": tipo,
                                    "Telefone": telefone,
                                    "CPF": cpf,
                                    "Email": email,
                                    "Endereço": endereco,
                                    "Status": "Cadastro Modificado"
                                }
                                df_participante_atualizado = pd.DataFrame([participante_atualizado])
                                atualizar_dados_participantes(df_participante_atualizado)
                                st.success("Participante atualizado com sucesso!")
                                time.sleep(2)
                                st.rerun()

                        if delete_button:
                            # Show a warning and require confirmation
                            st.warning("Atenção: Todos os dados associados ao participante, incluindo orçamentos, serão excluídos permanentemente.")
                            confirm_delete = st.checkbox(f"Confirmo que desejo excluir o participante {row['Nome']} e todos os dados associados.", key=f'confirm_delete_{index}')

                            if confirm_delete:
                                print(f"Deleting participant with ID: {row['id']}")
                                print(f"Deleting budgets associated with Tipo: {row["Tipo"]}")
                                deletar_dados_orcamentos(row["id"],row["Tipo"],part_id=int(row["id"]))
                                deletar_dados_participantes([row["id"]])
                                st.success("Participante e orçamentos associados deletados com sucesso!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.info("Marque a caixa de confirmação para prosseguir com a exclusão.")
        else:
            st.info("Nenhuma ação selecionada.")                
    else:
        st.warning("Nenhum cliente encontrado.")

