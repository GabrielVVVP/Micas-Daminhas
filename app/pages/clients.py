import streamlit as st
import pandas as pd
import datetime as dt
import time
from app.utils.helpers import get_db_connection, is_valid_telefone, is_valid_cpf, is_valid_email
from app.utils.eventos import *

def new_record():

    st.header("Cadastro Clientes")

    conn = get_db_connection()

    option = st.selectbox("Tipo de Ação", ["Novo Cliente", "Editar Cliente"])	

    if option == "Novo Cliente":
        st.markdown("### Novo Cliente")
        tipo_event = st.selectbox("Tipo de Evento", ["Casamento", "Formatura"])	

        with st.form(key='novo_cadastro_form'):
            if tipo_event == "Casamento":
                st.markdown(f"### Cadastro de Casamento")
                data_casamento = st.date_input("Data do Casamento")
                noiva = st.text_input("Noiva") 
                telefone = st.text_input("Telefone")
                email = st.text_input("Email") 
                endereco = st.text_input("Endereço")
                cpf_noiva = st.text_input("CPF da Noiva")
                tipo_evento = "Casamento"
                tipo_pagamento = st.selectbox("Tipo de Pagamento", ["Cliente Integral", "Individual"])
                
                submit_button = st.form_submit_button(label="Salvar Registro")  

                if submit_button:
                    if check_duplicate_event(conn, tipo_evento, noiva, data_casamento):
                        st.error("Já existe um evento com o mesmo tipo, nome e data no banco de dados.")
                    elif not is_valid_cpf(cpf_noiva):
                        st.error("CPF inválido. Certifique-se de que contém 11 dígitos.")
                    elif not is_valid_telefone(telefone):
                        st.error("Telefone inválido. Certifique-se de que contém 11 dígitos.") 
                    elif not is_valid_email(email):
                        st.error("Email inválido. Certifique-se de que está no formato correto.")    
                    else:
                        novo_registro = {
                            "Data": pd.to_datetime("now").date(),
                            "Data do Evento": data_casamento,
                            "Nome": noiva,
                            "Telefone": telefone,
                            "Email": email,  
                            "Endereço": endereco,
                            "CPF": cpf_noiva,
                            "Tipo Evento": tipo_evento,
                            "Tipo Pagamento": tipo_pagamento,
                            "Status": "Novo Cliente",
                        }
                        df_novo_registro = pd.DataFrame([novo_registro])
                        try:
                            save_cliente(df_novo_registro)
                            st.success("Registro salvo com sucesso!")
                            time.sleep(2)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar registro: {e}")
                            st.write("Detalhes do erro:", e)  # Output exception details for debugging

            elif tipo_event == "Formatura":
                st.markdown(f"### Cadastro de Formatura")  
                data_formatura = st.date_input("Data da Formatura")
                formando = st.text_input("Formando") 
                telefone = st.text_input("Telefone")
                email = st.text_input("Email")
                endereco = st.text_input("Endereço") 
                cpf_formando = st.text_input("CPF do Formando")
                tipo_pagamento = st.selectbox("Tipo de Pagamento", ["Cliente Integral", "Individual"])
                tipo_evento = "Formatura"

                submit_button = st.form_submit_button(label="Salvar Registro")   

                if submit_button:
                    if check_duplicate_event(conn, tipo_evento, formando, data_formatura):
                        st.error("Já existe um evento com o mesmo tipo, nome e data no banco de dados.")
                    elif not is_valid_cpf(cpf_formando):
                        st.error("CPF inválido. Certifique-se de que contém 11 dígitos.")
                    elif not is_valid_telefone(telefone):
                        st.error("Telefone inválido. Certifique-se de que contém 11 dígitos.")     
                    elif not is_valid_email(email):
                        st.error("Email inválido. Certifique-se de que está no formato correto.")    
                    else:
                        novo_registro = {
                            "Data": pd.to_datetime("now").date(),
                            "Data do Evento": data_formatura,
                            "Nome": formando,
                            "Telefone": telefone,
                            "Email": email,
                            "Endereço": endereco,
                            "CPF": cpf_formando,
                            "Tipo Evento": tipo_evento,
                            "Tipo Pagamento": tipo_pagamento,
                            "Status": "Novo Cliente",
                        }
                        df_novo_registro = pd.DataFrame([novo_registro])
                        try:
                            save_cliente(df_novo_registro)
                            st.success("Registro salvo com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar registro: {e}")
                            st.write("Detalhes do erro:", e)  # Output exception details for debugging
    else:
        clientes = get_clientes(conn)
        st.markdown("### Editar Clientes Existentes")
        min_date = pd.to_datetime(clientes["Data"], errors="coerce").min()
        max_date = pd.to_datetime(clientes["Data"], errors="coerce").max()
        fallback_date = dt.date.today()
        start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
        end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)
        filtered_clientes = clientes[
            (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
            (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
        ]
        cliente_selecionado = st.selectbox("Selecione um Cliente para Editar ou Deletar", filtered_clientes["Nome"] if not filtered_clientes.empty else [])
        if cliente_selecionado:
            cliente_info = filtered_clientes[filtered_clientes["Nome"] == cliente_selecionado].iloc[0]

            with st.form(key='editar_cliente_form'):
                st.markdown("### Editar Cliente")
                data_evento = st.date_input("Data do Evento", value=pd.to_datetime(cliente_info["Data"]))
                nome = st.text_input("Nome", value=cliente_info["Nome"])
                telefone = st.text_input("Telefone", value=cliente_info["Telefone"])
                email = st.text_input("Email", value=cliente_info["Email"])
                endereco = st.text_input("Endereço", value=cliente_info["Endereço"])
                cpf = st.text_input("CPF", value=cliente_info["CPF"])
                tipo_evento = st.selectbox("Tipo de Evento", ["Casamento", "Formatura"], index=["Casamento", "Formatura"].index(cliente_info["Tipo Evento"]))
                tipo_pagamento = st.selectbox("Tipo de Pagamento", ["Cliente Integral", "Individual"], index=["Cliente Integral", "Individual"].index(cliente_info["Tipo Pagamento"]), disabled=True)

                col1, col2 = st.columns(2)
                with col1:
                    update_button = st.form_submit_button(label="Atualizar Cliente")
                with col2:
                    delete_button = st.form_submit_button(label="Deletar Cliente")

                if update_button:
                    if not is_valid_cpf(cpf):
                        st.error("CPF inválido. Certifique-se de que contém 11 dígitos.")
                    elif not is_valid_telefone(telefone):
                        st.error("Telefone inválido. Certifique-se de que contém 11 dígitos.") 
                    elif not is_valid_email(email): 
                        st.error("Email inválido. Certifique-se de que está no formato correto.")    
                    else:    
                        update_cliente(
                            conn,
                            int(cliente_info["id"]),
                            data_evento,
                            nome,
                            telefone,
                            email,
                            endereco,
                            cpf,
                            tipo_evento,
                            tipo_pagamento,
                        )
                        st.success("Cliente atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()
                
                if delete_button:
                    st.warning("Atenção: Todos os dados associados ao participante, incluindo orçamentos, serão excluídos permanentemente.")
                    confirm_delete = st.checkbox(f"Confirmo que desejo excluir o participante {nome} e todos os dados associados.", key=f'confirm_delete_{cliente_info["id"]}')
                    if confirm_delete:
                        try:
                            st.info("Tentando deletar cliente e dados associados...")
                            delete_cliente_and_associated_data(int(cliente_info["id"]))
                            st.success("Cliente e dados associados deletados com sucesso!")
                            time.sleep(2)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao deletar cliente: {e}")
                            st.write("Detalhes do erro:", e)  
                        finally:
                            time.sleep(2)
                            st.info("Operação de exclusão concluída.")
                    else:
                        st.info("Marque a caixa de confirmação para prosseguir com a exclusão.")        
        else:
            st.warning("Nenhum cliente selecionado ou disponível para edição.")


