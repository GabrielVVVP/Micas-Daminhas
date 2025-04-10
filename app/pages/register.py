import streamlit as st
import pandas as pd
import time
import datetime as dt
from app.pages import report
from app.utils.caixa import salvar_dados_caixa, carregar_dados_caixa, deletar_dados_caixa, atualizar_dados_caixa

def new_record():
    st.header("Caixa Micas Daminhas")

    operacao = st.selectbox("Qual operação no caixa deseja fazer", ["Nenhum", "Relatório Financeiro", "Ver Caixa e Registros", "Adicionar Pagamento/Retirada", "Editar/Excluir Registros"])	

    if operacao == "Adicionar Pagamento/Retirada":
        with st.form(key='novo_registro_retirada_form'):
            st.markdown(f"### Novo Registro Caixa")
            data = st.date_input("Data", value=dt.date.today())
            observacao = st.selectbox("Selecione a origem do valor", ["Pagamento Avulso","Devolução", "Micas", "Micas Loja"])
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")
            operacao = st.selectbox("Operação", ["Entrada", "Saída"])	

            submit_button = st.form_submit_button(label="Salvar Registro")   

            if submit_button:
                novo_registro_retirada = {
                    "Participante_id": "Nenhum",
                    "Data": data,
                    "Observação": observacao,
                    "Valor": valor,
                    "Operação": operacao	
                }
                df_novo_registro_retirada = pd.DataFrame([novo_registro_retirada])
                salvar_dados_caixa(df_novo_registro_retirada)
                st.success("Registro salvo com sucesso!")
                time.sleep(2)
                st.rerun()
        st.warning("Atenção: Valores obtidos por pagamento das daminhas são retirados diretamente dos status dos orçamentos. Não é possível inserir um pagamento por daminha por aqui.")        
    elif operacao == "Editar/Excluir Registros":
        st.markdown(f"### Editar/Excluir Registros")

        opcoes_tipo_edicao = st.selectbox("Selecione um tipo de visualização", ["Um Registro", "Diversos Registros"])
        if opcoes_tipo_edicao == "Um Registro":
            registros = carregar_dados_caixa()
            min_date = pd.to_datetime(registros["Data"], errors="coerce").min()
            max_date = pd.to_datetime(registros["Data"], errors="coerce").max()
            fallback_date = dt.date.today()
            start_date = st.date_input("Data Inicial", value=min_date.date() if pd.notna(min_date) else fallback_date)
            end_date = st.date_input("Data Final", value=max_date.date() if pd.notna(max_date) else fallback_date)
            filtered_registros = registros[
                (pd.to_datetime(registros["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
                (pd.to_datetime(registros["Data"], errors="coerce") <= pd.to_datetime(end_date))
            ]

            # Display the records in a table
            st.dataframe(registros)

            # Select a record to edit or delete
            selected_record = st.selectbox("Selecione um registro para editar/excluir", filtered_registros["Observação"].tolist() if not filtered_registros.empty else [])

            if selected_record is not None:
                record_to_edit = registros[registros["Observação"] == selected_record]
                st.write("Registro Selecionado:")
                st.write(record_to_edit)

                # Edit form
                with st.form(key='edit_record_form'):
                    data = st.date_input("Data", value=pd.to_datetime(record_to_edit["Data"].iloc[0]).date())
                    observacao = st.text_input("Observação", value=record_to_edit["Observação"].iloc[0])
                    valor = st.number_input("Valor", value=record_to_edit["Valor"].iloc[0], min_value=0.0, format="%.2f")
                    operacao = st.selectbox(
                        "Operação", 
                        ["Entrada", "Saída"], 
                        index=["Entrada", "Saída"].index(record_to_edit["Operação"].iloc[0])
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button(label="Atualizar Registro")
                    with col2:
                        delete_button = st.form_submit_button(label="Excluir Registro")

                    if update_button:
                        updated_record = {
                            "id": record_to_edit["id"].iloc[0],
                            "Data": data,
                            "Observação": observacao,
                            "Valor": valor,
                            "Operação": operacao	
                        }
                        df_updated_record = pd.DataFrame([updated_record])
                        atualizar_dados_caixa(df_updated_record)
                        st.success("Registro atualizado com sucesso!")
                        time.sleep(2)
                        st.rerun()

                    # Delete button
                    if delete_button:
                        delete_confirmation = st.checkbox("Tem certeza que deseja excluir este registro?", value=False)
                        if delete_confirmation:
                            deletar_dados_caixa((int(record_to_edit["id"].iloc[0]),))
                            st.success("Registro excluído com sucesso!")
                            time.sleep(2)
                            st.rerun()
            else:
                st.warning("Nenhum registro selecionado. Por favor, selecione um registro para editar ou excluir.")                

        elif opcoes_tipo_edicao == "Diversos Registros":
            registros = carregar_dados_caixa()
            filtered_registros = registros

            opcoes_data = st.selectbox("Selecione um filtro de datas", ["Tudo", "Datas Específicas"])
            if opcoes_data == "Datas Específicas":
                min_date = pd.to_datetime(registros["Data"], errors="coerce").min()
                max_date = pd.to_datetime(registros["Data"], errors="coerce").max()
                fallback_date = dt.date.today()
                start_date = st.date_input("Data Inicial", value=min_date.date() if pd.notna(min_date) else fallback_date)
                end_date = st.date_input("Data Final", value=max_date.date() if pd.notna(max_date) else fallback_date)
                filtered_registros = registros[
                    (pd.to_datetime(registros["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
                    (pd.to_datetime(registros["Data"], errors="coerce") <= pd.to_datetime(end_date))
                ]

            opcoes_registros = st.selectbox("Selecione uma opção de caixa", ["Todos", "Entradas", "Saídas"])
            if opcoes_registros == "Entradas":
                filtered_registros = filtered_registros[filtered_registros["Operação"] == "Entrada"]
            elif opcoes_registros == "Saídas":
                filtered_registros = filtered_registros[filtered_registros["Operação"] == "Saída"]
            
            filtered_registros['Deletar'] = False
            edited_df = st.data_editor(filtered_registros, use_container_width=True)
            
            if st.button("Salvar Alterações"):
                atualizar_dados_caixa(edited_df)
                st.success("Dados atualizados com sucesso!")
                time.sleep(2)
                st.rerun()

            # Delete selected records
            if st.button("Deletar Registros Selecionados"):
                st.session_state['confirm_delete'] = True
                st.warning("Se deletados, os dados não podem ser recuperados. Pressione 'Confirmar Deleção' para deletar.")
                
            if st.session_state.get('confirm_delete', False) and st.button("Confirmar Deleção"):    
                ids_to_delete = edited_df[edited_df['Deletar'] == True]['id'].tolist()
                if ids_to_delete:
                    deletar_dados_caixa(ids_to_delete)
                    st.success("Registros deletados com sucesso!")
                    st.session_state['confirm_delete'] = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("Nenhum registro selecionado para deletar.")
        
    elif operacao == "Ver Caixa e Registros":
        st.markdown(f"### Ver Caixa e Registros")
        
        registros = carregar_dados_caixa()
        filtered_registros = registros
        start_date = pd.to_datetime(registros["Data"], errors="coerce").min()
        end_date = pd.to_datetime(registros["Data"], errors="coerce").max()

        opcoes_data = st.selectbox("Selecione uma opção", ["Tudo", "Datas Específicas"])
        if opcoes_data == "Datas Específicas":
            fallback_date = dt.date.today()
            start_date = st.date_input("Data Inicial", value=start_date.date() if pd.notna(start_date) else fallback_date)
            end_date = st.date_input("Data Final", value=end_date.date() if pd.notna(end_date) else fallback_date)
            filtered_registros = registros[
                (pd.to_datetime(registros["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
                (pd.to_datetime(registros["Data"], errors="coerce") <= pd.to_datetime(end_date))
            ]

        opcoes_registros = st.selectbox("Selecione uma opção", ["Todos", "Entradas", "Saídas"])
        if opcoes_registros == "Entradas":
            filtered_registros = filtered_registros[filtered_registros["Operação"] == "Entrada"]
        elif opcoes_registros == "Saídas":
            filtered_registros = filtered_registros[filtered_registros["Operação"] == "Saída"]
        
        st.dataframe(filtered_registros, use_container_width=True)

        # Calculate and display total values
        total_entrada = filtered_registros[filtered_registros["Operação"] == "Entrada"]["Valor"].sum()
        total_saida = filtered_registros[filtered_registros["Operação"] == "Saída"]["Valor"].sum()
        saldo = total_entrada - total_saida

        if opcoes_registros == "Entradas":
            with st.container(border=True):
                st.markdown(f"Caixa Micas Daminhas")
                if opcoes_data == "Datas Específicas":
                    st.write(f"*Data Inicial:* {start_date}")
                    st.write(f"*Data Final:* {end_date}")
                st.write(f"*Total de Entradas:* R$ {total_entrada:.2f}")
        elif opcoes_registros == "Saídas":        
            with st.container(border=True):
                st.markdown(f"Caixa Micas Daminhas")
                st.write(f"*Data Inicial:* {start_date}")
                st.write(f"*Data Final:* {end_date}")
                st.write(f"*Total de Saídas:* R$ {total_saida:.2f}")
        else:
            with st.container(border=True):
                st.markdown(f"Caixa Micas Daminhas")
                st.write(f"*Data Inicial:* {start_date}")
                st.write(f"*Data Final:* {end_date}")
                st.write(f"*Total de Entradas:* R$ {total_entrada:.2f}")
                st.write(f"*Total de Saídas:* R$ {total_saida:.2f}")
                st.write(f"*Saldo:* R$ {saldo:.2f}")
                st.write(f"*Total de Registros:* {len(filtered_registros)}")        
    elif operacao == "Relatório Financeiro":
        report.display_report()
    else:
        st.info("Selecione uma operação para continuar.")

