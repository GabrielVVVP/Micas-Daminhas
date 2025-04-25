import streamlit as st
import pandas as pd
import time
import os
import datetime as dt
from streamlit_pdf_viewer import pdf_viewer
from assets.metadata.meta import dados_micas
from app.utils.helpers import get_db_connection
from app.utils.pdf import gerar_contrato_devolucao_pdf, gerar_contrato_retirada_pdf, gerar_contrato_retirada_todos_pdf, gerar_contrato_devolucao_todos_pdf
from app.utils.orcamentos import get_eventos, get_participantes, get_orcamento, get_orcamentos, update_status_multiple_orcamento

def contracts():
    st.header("Contratos de Retirada/Devolução")	

    if "show_pdf" not in st.session_state:
        st.session_state["show_pdf"] = False

    conn = get_db_connection()
    clientes = get_eventos(conn)
    
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
    elif date_option == "Seletor de Datas":
        start_date = st.date_input("Data Inicial", value=min_date if pd.notna(min_date) else fallback_date)
        end_date = st.date_input("Data Final", value=max_date if pd.notna(max_date) else fallback_date)
        
    filtered_clientes = clientes[
        (pd.to_datetime(clientes["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
        (pd.to_datetime(clientes["Data"], errors="coerce") <= pd.to_datetime(end_date))
    ]

    cliente_selecionado = st.selectbox("Selecione o Cliente", filtered_clientes["Nome"] if not filtered_clientes.empty else [])
    if clientes.empty:
        st.warning("Nenhum cliente encontrado.")
        return
    if filtered_clientes.empty:
        st.warning("Nenhum cliente encontrado para o intervalo de datas selecionado.")
        
    cliente_dados = clientes[clientes["Nome"] == cliente_selecionado].iloc[0]
    evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]

    participantes = get_participantes(conn, evento_id)
    if participantes.empty:
        st.warning("Nenhum participante encontrado para o cliente selecionado.")
        return
    if cliente_dados["Tipo Pagamento"] == "Cliente Integral":
        participantes_dados_df = participantes.copy()
        participantes_dados_df_2 = participantes.copy()
        participantes_dados_df = participantes_dados_df.drop(columns=["Evento_id", "id"], errors="ignore")
        participantes_dados_df.insert(2, "Nome do Cliente", cliente_dados["Nome"])
        st.write("#### Dados do Participantes")
        st.dataframe(participantes_dados_df)
        orcamento_meninas, orcamento_meninos = get_orcamentos(evento_id)

        if (not orcamento_meninas.empty) or (not orcamento_meninos.empty):
            st.markdown("### Dados do Orçamento das Meninas")
            if not orcamento_meninas.empty:
                orcamentos_meninas_completo = orcamento_meninas.copy()
                participantes_dict = participantes_dados_df_2.set_index("id")["Nome"].to_dict()
                orcamento_meninas["Participante_id"] = orcamento_meninas["Participante_id"].map(participantes_dict)
                orcamento_meninas = orcamento_meninas.drop(columns=["Evento_id", "id"], errors="ignore")
                orcamento_meninas.insert(1, "Nome do Cliente", cliente_dados["Nome"])
                orcamento_meninas.insert(2, "Nome do Participante", orcamento_meninas["Participante_id"])
                orcamento_meninas = orcamento_meninas.drop(columns=["Participante_id"], errors="ignore")
                status_contrato_retirada = orcamento_meninas["Status Contrato Retirada"].loc[0] if not orcamento_meninas.empty else None
                status_contrato_devolucao = orcamento_meninas["Status Contrato Devolução"].loc[0] if not orcamento_meninas.empty else None
                st.write(orcamento_meninas)
            else:
                st.warning("Nenhum orçamento encontrado para as meninas.")    
            st.markdown("### Dados do Orçamento dos Meninos")
            if not orcamento_meninos.empty:
                orcamentos_meninos_completo = orcamento_meninos.copy()
                participantes_dict = participantes_dados_df_2.set_index("id")["Nome"].to_dict()
                orcamento_meninos["Participante_id"] = orcamento_meninos["Participante_id"].map(participantes_dict)
                orcamento_meninos = orcamento_meninos.drop(columns=["Evento_id", "id"], errors="ignore")
                orcamento_meninos.insert(1, "Nome do Cliente", cliente_dados["Nome"])
                orcamento_meninos.insert(2, "Nome do Participante", orcamento_meninos["Participante_id"])
                orcamento_meninos = orcamento_meninos.drop(columns=["Participante_id"], errors="ignore")
                status_contrato_retirada = orcamento_meninos["Status Contrato Retirada"].loc[0] if not orcamento_meninos.empty else None
                status_contrato_devolucao = orcamento_meninos["Status Contrato Devolução"].loc[0] if not orcamento_meninos.empty else None
                st.write(orcamento_meninos)
            else:
                st.warning("Nenhum orçamento encontrado para os meninos.")    

            dataframes = [df for df in [orcamento_meninas, orcamento_meninos] if not df.empty and not df.isna().all().all()]
            orcamentos = pd.concat(dataframes, ignore_index=True)

            st.info("**Atenção:** O contrato de devolução só pode ser gerado após a assinatura do contrato de retirada.")

            with st.container(border=True):
                st.markdown("### Contrato de Retirada")
                if status_contrato_retirada == "Contrato Assinado":
                    st.success("Contrato de Retirada já está assinado. Não é mais possível modificá-lo.")
                elif status_contrato_retirada == "Contrato Emitido":
                    st.info("Contrato de Retirada já foi emitido.")
                else:
                    st.warning("Contrato de Retirada ainda não foi emitido.")
                if st.button("Gerar Contrato de Retirada", disabled=(status_contrato_retirada == "Contrato Assinado")):
                    dados_contrato = {
                        "contratante_nome": cliente_dados["Nome"],
                        "contratante_cpf": cliente_dados["CPF"],
                        "contratante_endereco": cliente_dados["Endereço"],
                        "contratante_telefone": cliente_dados["Telefone"],
                        "contratante_email": cliente_dados["Email"],
                        "contratada_nome": dados_micas["Contratada Nome"],
                        "contratada_cnpj": dados_micas["Contratada CNPJ"],
                        "contratada_endereco": dados_micas["Contratada Endereco"],
                        "contratada_telefone": dados_micas["Contratada Telefone"],
                        "contratada_whatsapp": dados_micas["Contratada Whatsapp"],
                        "contratada_email": dados_micas["Contratada Email"],
                        "descricao_roupa": orcamentos["Modelo"],
                        "acessorios": orcamentos["Acessórios"],
                        "obs": orcamentos["Observação"],
                        "estado_retirada": orcamentos["Estado Retirada"],
                        "valor_aluguel": orcamentos["Valor Total"],
                        "valor_desc": orcamentos["Taxa de Desconto"],
                        "valor_aluguel_desc": orcamentos["Valor com Desconto"],
                        "data_retirada": orcamentos["Data Retirada"],
                        "data_devolucao": orcamentos["Data Devolução"]
                    }
                    pdf_path = gerar_contrato_retirada_todos_pdf(dados_contrato)
                    update_status_multiple_orcamento(int(evento_id), "Contrato Retirada", pdf_path)
                    update_status_multiple_orcamento(int(evento_id), "Status Contrato Retirada", "Contrato Emitido")
                    st.success("Contrato gerado com sucesso em: " + pdf_path)
                    time.sleep(2)
                    st.rerun()

                # Checkbox for signing the contract of retirada
                if status_contrato_retirada == "Contrato Emitido":
                    pdf_path = orcamentos.loc[0]["Contrato Retirada"]
                    if st.button("Mostrar/Ocultar Contrato de Retirada Emitido"):
                        st.session_state["show_pdf"] = not st.session_state["show_pdf"]
                    if st.session_state["show_pdf"]:
                        if pdf_path and os.path.exists(pdf_path):
                            pdf_viewer(pdf_path)
                        else:
                            st.error("O caminho do PDF é inválido ou o arquivo não foi encontrado.")
                    if st.checkbox("Assinar Contrato de Retirada"):
                        status_contrato_retirada = "Contrato Assinado"
                        update_status_multiple_orcamento(int(evento_id), "Status Contrato Retirada", "Contrato Assinado")
                        st.success("Contrato de Retirada assinado com sucesso!")
                        time.sleep(2)
                        st.rerun() 
            with st.container(border=True):
                st.markdown("### Contrato de Devolução")
                if status_contrato_devolucao == "Contrato Assinado":
                    st.success("Contrato de Devolução já está assinado. Não é mais possível modificá-lo.")
                elif status_contrato_devolucao == "Contrato Emitido":
                    st.info("Contrato de Devolução já foi emitido.")
                else:
                    st.warning("Contrato de Devolução ainda não foi emitido.")
                if st.button("Gerar Contrato de Devolução", disabled=((status_contrato_devolucao == "Contrato Assinado")or(status_contrato_retirada != "Contrato Assinado"))):
                    dados_contrato = {
                        "contratante_nome": cliente_dados["Nome"],
                        "contratante_cpf": cliente_dados["CPF"],
                        "contratante_endereco": cliente_dados["Endereço"],
                        "contratante_telefone": cliente_dados["Telefone"],
                        "contratante_email": cliente_dados["Email"],
                        "contratada_nome": dados_micas["Contratada Nome"],
                        "contratada_cnpj": dados_micas["Contratada CNPJ"],
                        "contratada_endereco": dados_micas["Contratada Endereco"],
                        "contratada_telefone": dados_micas["Contratada Telefone"],
                        "contratada_whatsapp": dados_micas["Contratada Whatsapp"],
                        "contratada_email": dados_micas["Contratada Email"],
                        "descricao_roupa": orcamentos["Modelo"],
                        "acessorios": orcamentos["Acessórios"],
                        "obs": orcamentos["Observação"],
                        "estado_devolucao": orcamentos["Estado Devolução"],
                        "valor_aluguel": orcamentos["Valor Total"],
                        "valor_desc": orcamentos["Taxa de Desconto"],
                        "valor_aluguel_desc": orcamentos["Valor com Desconto"],
                        "data_retirada": orcamentos["Data Retirada"],
                        "data_devolucao": orcamentos["Data Devolução"]
                    }
                    pdf_path = gerar_contrato_devolucao_todos_pdf(dados_contrato)
                    update_status_multiple_orcamento(int(evento_id), "Contrato Devolução", pdf_path)
                    update_status_multiple_orcamento(int(evento_id), "Status Contrato Devolução", "Contrato Emitido")
                    st.success("Contrato gerado com sucesso em: " + pdf_path)
                    time.sleep(2)
                    st.rerun()        

                # Checkbox for signing the contract of devolução
                if status_contrato_devolucao == "Contrato Emitido":
                    pdf_path = orcamentos.loc[0]["Contrato Devolução"]
                    if st.button("Mostrar/Ocultar Contrato de Devolução Emitido"):
                        st.session_state["show_pdf"] = not st.session_state["show_pdf"]
                    if st.session_state["show_pdf"]:
                        st.info(pdf_path)
                        if pdf_path and os.path.exists(pdf_path):
                            pdf_viewer(pdf_path)
                        else:
                            st.error("O caminho do PDF é inválido ou o arquivo não foi encontrado.")
                    if st.checkbox("Assinar Contrato de Devolução"):
                        status_contrato_devolucao = "Contrato Assinado"
                        update_status_multiple_orcamento(int(evento_id), "Status Contrato Devolução", "Contrato Assinado")
                        st.success("Contrato de Devolução assinado com sucesso!")
                        time.sleep(2)
                        st.rerun() 
        else:
            st.warning("Nenhum orçamento encontrado para o participante selecionado.")

    else:    
        participante_selecionado = st.selectbox("Selecione o Participante", participantes["Nome"])
        participante_id = participantes[participantes["Nome"] == participante_selecionado]["id"].values[0]
        participante_dados = participantes[participantes["Nome"] == participante_selecionado].iloc[0]
        
        orcamento = get_orcamento(conn, evento_id, participante_id, participante_dados["Tipo"])

        participante_dados_df = participante_dados.to_frame().T
        participante_dados_df = participante_dados_df.drop(columns=["Evento_id", "id"], errors="ignore")
        participante_dados_df.insert(0, "Nome do Cliente", cliente_dados["Nome"])
        st.write("#### Dados do Participante")
        st.write(participante_dados_df.T)

        if not orcamento.empty:
            orcamento_completo = orcamento.copy()
            participantes_dict = participantes.set_index("id")["Nome"].to_dict()
            orcamento["Participante_id"] = orcamento["Participante_id"].map(participantes_dict)
            orcamento = orcamento.drop(columns=["Evento_id", "id"], errors="ignore")
            orcamento.insert(1, "Nome do Cliente", cliente_dados["Nome"])
            orcamento.insert(2, "Nome do Participante", orcamento["Participante_id"])
            orcamento = orcamento.drop(columns=["Participante_id"], errors="ignore")
            status_contrato_retirada = orcamento.loc[0]["Status Contrato Retirada"] if not orcamento.empty else None
            status_contrato_devolucao = orcamento.loc[0]["Status Contrato Devolução"] if not orcamento.empty else None
            
            # Ensure consistent data types for all columns
            orcamento_table = orcamento.astype(str)
            
            st.markdown("### Dados do Orçamento")
            st.write(orcamento_table.T)

            st.info("**Atenção:** O contrato de devolução só pode ser gerado após a assinatura do contrato de retirada.")

            with st.container(border=True):
                st.markdown("### Contrato de Retirada")
                if status_contrato_retirada == "Contrato Assinado":
                    st.success("Contrato de Retirada já está assinado. Não é mais possível modificá-lo.")
                elif status_contrato_retirada == "Contrato Emitido":
                    st.info("Contrato de Retirada já foi emitido.")
                else:
                    st.warning("Contrato de Retirada ainda não foi emitido.")
                if st.button("Gerar Contrato de Retirada", disabled=(status_contrato_retirada == "Contrato Assinado")):
                    dados_contrato = {
                        "contratante_nome": cliente_dados["Nome"],
                        "participante_nome": orcamento.loc[0]["Nome do Participante"],
                        "contratante_cpf": cliente_dados["CPF"],
                        "contratante_endereco": cliente_dados["Endereço"],
                        "contratante_telefone": cliente_dados["Telefone"],
                        "contratante_email": cliente_dados["Email"],
                        "contratada_nome": dados_micas["Contratada Nome"],
                        "contratada_cnpj": dados_micas["Contratada CNPJ"],
                        "contratada_endereco": dados_micas["Contratada Endereco"],
                        "contratada_telefone": dados_micas["Contratada Telefone"],
                        "contratada_whatsapp": dados_micas["Contratada Whatsapp"],
                        "contratada_email": dados_micas["Contratada Email"],
                        "descricao_roupa": orcamento.loc[0]["Modelo"],
                        "acessorios": orcamento.loc[0]["Acessórios"],
                        "obs": orcamento.loc[0]["Observação"],
                        "estado_retirada": orcamento.loc[0]["Estado Retirada"],
                        "valor_aluguel": orcamento.loc[0]["Valor Total"],
                        "valor_desc": orcamento.loc[0]["Taxa de Desconto"],
                        "valor_aluguel_desc": orcamento.loc[0]["Valor com Desconto"],
                        "data_retirada": orcamento.loc[0]["Data Retirada"],
                        "data_devolucao": orcamento.loc[0]["Data Devolução"]
                    }
                    pdf_path = gerar_contrato_retirada_pdf(dados_contrato)
                    conn.execute(
                        f"UPDATE orcamentos_meninos SET `Contrato Retirada` = '{pdf_path}', `Status Contrato Retirada` = 'Contrato Emitido' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                        if participante_dados["Tipo"] == "Menino"
                        else f"UPDATE orcamentos_meninas SET `Contrato Retirada` = '{pdf_path}', `Status Contrato Retirada` = 'Contrato Emitido' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                    )
                    conn.commit()
                    st.success("Contrato gerado com sucesso em: " + pdf_path)
                    time.sleep(2)
                    st.rerun()

                # Checkbox for signing the contract of retirada
                if status_contrato_retirada == "Contrato Emitido":
                    pdf_path = orcamento.loc[0]["Contrato Retirada"]
                    if st.button("Mostrar/Ocultar Contrato de Retirada Emitido"):
                        st.session_state["show_pdf"] = not st.session_state["show_pdf"]
                    if st.session_state["show_pdf"]:
                        if pdf_path and os.path.exists(pdf_path):
                            pdf_viewer(pdf_path)
                        else:
                            st.error("O caminho do PDF é inválido ou o arquivo não foi encontrado.")
                    if st.checkbox("Assinar Contrato de Retirada"):
                        status_contrato_retirada = "Contrato Assinado"
                        conn.execute(
                            f"UPDATE orcamentos_meninos SET `Status Contrato Retirada` = 'Contrato Assinado' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                            if participante_dados["Tipo"] == "Menino"
                            else f"UPDATE orcamentos_meninas SET `Status Contrato Retirada` = 'Contrato Assinado' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                        )
                        conn.commit()
                        st.success("Contrato de Retirada assinado com sucesso!")
                        time.sleep(2)
                        st.rerun() 
            with st.container(border=True):
                st.markdown("### Contrato de Devolução")
                if status_contrato_devolucao == "Contrato Assinado":
                    st.success("Contrato de Devolução já está assinado. Não é mais possível modificá-lo.")
                elif status_contrato_devolucao == "Contrato Emitido":
                    st.info("Contrato de Devolução já foi emitido.")
                else:
                    st.warning("Contrato de Devolução ainda não foi emitido.")
                if st.button("Gerar Contrato de Devolução", disabled=((status_contrato_devolucao == "Contrato Assinado")or(status_contrato_retirada != "Contrato Assinado"))):
                    dados_contrato = {
                        "contratante_nome": cliente_dados["Nome"],
                        "participante_nome": orcamento.loc[0]["Nome do Participante"],
                        "contratante_cpf": cliente_dados["CPF"],
                        "contratante_endereco": cliente_dados["Endereço"],
                        "contratante_telefone": cliente_dados["Telefone"],
                        "contratante_email": cliente_dados["Email"],
                        "contratada_nome": dados_micas["Contratada Nome"],
                        "contratada_cnpj": dados_micas["Contratada CNPJ"],
                        "contratada_endereco": dados_micas["Contratada Endereco"],
                        "contratada_telefone": dados_micas["Contratada Telefone"],
                        "contratada_whatsapp": dados_micas["Contratada Whatsapp"],
                        "contratada_email": dados_micas["Contratada Email"],
                        "descricao_roupa": orcamento.loc[0]["Modelo"],
                        "acessorios": orcamento.loc[0]["Acessórios"],
                        "obs": orcamento.loc[0]["Observação"],
                        "estado_devolucao": orcamento.loc[0]["Estado Devolução"],
                        "valor_aluguel": orcamento.loc[0]["Valor Total"],
                        "valor_desc": orcamento.loc[0]["Taxa de Desconto"],
                        "valor_aluguel_desc": orcamento.loc[0]["Valor com Desconto"],
                        "data_retirada": orcamento.loc[0]["Data Retirada"],
                        "data_devolucao": orcamento.loc[0]["Data Devolução"]
                    }
                    pdf_path = gerar_contrato_devolucao_pdf(dados_contrato)
                    conn.execute(
                        f"UPDATE orcamentos_meninos SET `Contrato Devolução` = '{pdf_path}', `Status Contrato Devolução` = 'Contrato Emitido' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                        if participante_dados["Tipo"] == "Menino"
                        else f"UPDATE orcamentos_meninas SET `Contrato Devolução` = '{pdf_path}', `Status Contrato Devolução` = 'Contrato Emitido' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                    )
                    conn.commit()
                    st.success("Contrato gerado com sucesso em: " + pdf_path)
                    time.sleep(2)
                    st.rerun()        

                # Checkbox for signing the contract of devolução
                if status_contrato_devolucao == "Contrato Emitido":
                    pdf_path = orcamento.loc[0]["Contrato Devolução"]
                    if st.button("Mostrar/Ocultar Contrato de Retirada Emitido"):
                        st.session_state["show_pdf"] = not st.session_state["show_pdf"]
                    if st.session_state["show_pdf"]:
                        if pdf_path and os.path.exists(pdf_path):
                            pdf_viewer(pdf_path)
                        else:
                            st.error("O caminho do PDF é inválido ou o arquivo não foi encontrado.")
                    if st.checkbox("Assinar Contrato de Devolução"):
                        status_contrato_devolucao = "Contrato Assinado"
                        conn.execute(
                            f"UPDATE orcamentos_meninos SET `Status Contrato Devolução` = 'Contrato Assinado' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                            if participante_dados["Tipo"] == "Menino"
                            else f"UPDATE orcamentos_meninas SET `Status Contrato Devolução` = 'Contrato Assinado' WHERE id = {int(orcamento_completo.loc[0]['id'])}"
                        )
                        conn.commit()
                        st.success("Contrato de Devolução assinado com sucesso!")
                        time.sleep(2)
                        st.rerun() 
        else:
            st.warning("Nenhum orçamento encontrado para o participante selecionado.")

