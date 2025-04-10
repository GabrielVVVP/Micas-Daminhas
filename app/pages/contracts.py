import streamlit as st
import pandas as pd
import time
from assets.metadata.meta import dados_micas
from app.utils.helpers import get_db_connection
from app.utils.pdf import gerar_contrato_devolucao_pdf, gerar_contrato_retirada_pdf
from app.utils.orcamentos import get_eventos, get_participantes, get_orcamento

def contracts():
    st.header("Contratos de Entrega/Retirada")	

    conn = get_db_connection()
    clientes = get_eventos(conn)
    if clientes.empty:
        st.warning("Nenhum cliente encontrado.")
        return

    cliente_selecionado = st.selectbox("Selecione o Cliente", clientes["Nome"])
    evento_id = clientes[clientes["Nome"] == cliente_selecionado]["id"].values[0]

    participantes = get_participantes(conn, evento_id)
    if participantes.empty:
        st.warning("Nenhum participante encontrado para o cliente selecionado.")
        return

    participante_selecionado = st.selectbox("Selecione o Participante", participantes["Nome"])
    participante_id = participantes[participantes["Nome"] == participante_selecionado]["id"].values[0]
    participante_dados = participantes[participantes["Nome"] == participante_selecionado].iloc[0]
    cliente_dados = clientes[clientes["Nome"] == cliente_selecionado].iloc[0]
    
    orcamento = get_orcamento(conn, evento_id, participante_id, participante_dados["Tipo"])

    participante_dados_df = participante_dados.to_frame().T
    participante_dados_df = participante_dados_df.drop(columns=["Evento_id", "id"], errors="ignore")
    participante_dados_df.insert(0, "Nome do Cliente", cliente_dados["Nome"])
    st.write("#### Dados do Participante")
    st.write(participante_dados_df.T)

    if not orcamento.empty:
        orcamento_completo = orcamento.copy()
        orcamento = orcamento.drop(columns=["Evento_id", "id"], errors="ignore")
        orcamento.insert(0, "Nome do Cliente", cliente_dados["Nome"])
        orcamento.insert(1, "Nome do Participante", participante_dados_df["Nome"])
        status_contrato_retirada = orcamento.loc[0]["Status Contrato Retirada"] if not orcamento.empty else None
        status_contrato_devolucao = orcamento.loc[0]["Status Contrato Devolução"] if not orcamento.empty else None
        st.markdown("### Dados do Orçamento")
        st.write(orcamento.T)

        if participante_dados["Responsável Financeiro"] == "Não Definido":    
            st.warning("**Atenção:** O responsável financeiro não está definido. Por favor, defina o responsável financeiro para gerar os contratos.")
        else:

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
                        "evento_id": evento_id,
                        "participante_id": participante_id,
                        "contratante_nome": participante_dados["Responsável Financeiro"],
                        "contratante_cpf": participante_dados["CPF"],
                        "contratante_endereco": participante_dados["Endereço"],
                        "contratante_telefone": participante_dados["Telefone"],
                        "contratante_email": participante_dados["Email"],
                        "contratada_nome": dados_micas["Contratada Nome"],
                        "contratada_cnpj": dados_micas["Contratada CNPJ"],
                        "contratada_endereco": dados_micas["Contratada Endereco"],
                        "contratada_telefone": dados_micas["Contratada Telefone"],
                        "contratada_email": dados_micas["Contratada Email"],
                        "descricao_roupa": orcamento.loc[0]["Modelo"],
                        "acessorios": orcamento.loc[0]["Acessórios"],
                        "obs": orcamento.loc[0]["Observação"],
                        "estado_retirada": "Perfeito estado",
                        "valor_aluguel": orcamento.loc[0]["Valor Total"],
                        "data_retirada": "15/03/2025",
                        "data_devolucao": "20/03/2025"
                    }
                    pdf_path = gerar_contrato_retirada_pdf(dados_contrato)
                    conn.execute(
                        f"UPDATE orcamentos_meninos SET `Contrato Retirada` = '{pdf_path}', `Status Contrato Retirada` = 'Contrato Emitido' WHERE id = {orcamento_completo.loc[0]['id']}"
                        if participante_dados["Tipo"] == "Menino"
                        else f"UPDATE orcamentos_meninas SET `Contrato Retirada` = '{pdf_path}', `Status Contrato Retirada` = 'Contrato Emitido' WHERE id = {orcamento_completo.loc[0]['id']}"
                    )
                    conn.commit()
                    st.success("Contrato gerado com sucesso em: " + pdf_path)
                    time.sleep(2)
                    st.rerun()

                # Checkbox for signing the contract of retirada
                if status_contrato_retirada == "Contrato Emitido":
                    st.markdown(f"[Visualizar Contrato de Retirada]({orcamento_completo.loc[0]['Contrato Retirada']})", unsafe_allow_html=True)
                    if st.checkbox("Assinar Contrato de Retirada"):
                        status_contrato_retirada = "Contrato Assinado"
                        conn.execute(
                            f"UPDATE orcamentos_meninos SET `Status Contrato Retirada` = 'Contrato Assinado' WHERE id = {orcamento_completo.loc[0]['id']}"
                            if participante_dados["Tipo"] == "Menino"
                            else f"UPDATE orcamentos_meninas SET `Status Contrato Retirada` = 'Contrato Assinado' WHERE id = {orcamento_completo.loc[0]['id']}"
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
                        "evento_id": evento_id,
                        "participante_id": participante_id,
                        "contratante_nome": participante_dados["Responsável Financeiro"],
                        "contratante_cpf": participante_dados["CPF"],
                        "contratante_endereco": participante_dados["Endereço"],
                        "contratante_telefone": participante_dados["Telefone"],
                        "contratante_email": participante_dados["Email"],
                        "contratada_nome": dados_micas["Contratada Nome"],
                        "contratada_cnpj": dados_micas["Contratada CNPJ"],
                        "contratada_endereco": dados_micas["Contratada Endereco"],
                        "contratada_telefone": dados_micas["Contratada Telefone"],
                        "contratada_email": dados_micas["Contratada Email"],
                        "descricao_roupa": orcamento.loc[0]["Modelo"],
                        "acessorios": orcamento.loc[0]["Acessórios"],
                        "obs": orcamento.loc[0]["Observação"],
                        "estado_devolucao": "Perfeito estado",
                        "valor_aluguel": orcamento.loc[0]["Valor Total"],
                        "data_retirada": "15/03/2025",
                        "data_devolucao": "20/03/2025"
                    }
                    pdf_path = gerar_contrato_devolucao_pdf(dados_contrato)
                    conn.execute(
                        f"UPDATE orcamentos_meninos SET `Contrato Devolução` = '{pdf_path}', `Status Contrato Devolução` = 'Contrato Emitido' WHERE id = {orcamento_completo.loc[0]['id']}"
                        if participante_dados["Tipo"] == "Menino"
                        else f"UPDATE orcamentos_meninas SET `Contrato Devolução` = '{pdf_path}', `Status Contrato Devolução` = 'Contrato Emitido' WHERE id = {orcamento_completo.loc[0]['id']}"
                    )
                    conn.commit()
                    st.success("Contrato gerado com sucesso em: " + pdf_path)
                    time.sleep(2)
                    st.rerun()        

                # Checkbox for signing the contract of devolução
                if status_contrato_devolucao == "Contrato Emitido":
                    st.write(f"[Visualizar Contrato de Devolução]({orcamento_completo.loc[0]['Contrato Devolução']})")
                    if st.checkbox("Assinar Contrato de Devolução"):
                        status_contrato_devolucao = "Contrato Assinado"
                        conn.execute(
                            f"UPDATE orcamentos_meninos SET `Status Contrato Devolução` = 'Contrato Assinado' WHERE id = {orcamento_completo.loc[0]['id']}"
                            if participante_dados["Tipo"] == "Menino"
                            else f"UPDATE orcamentos_meninas SET `Status Contrato Devolução` = 'Contrato Assinado' WHERE id = {orcamento_completo.loc[0]['id']}"
                        )
                        conn.commit()
                        st.success("Contrato de Devolução assinado com sucesso!")
                        time.sleep(2)
                        st.rerun() 
    else:
        st.warning("Nenhum orçamento encontrado para o participante selecionado.")

