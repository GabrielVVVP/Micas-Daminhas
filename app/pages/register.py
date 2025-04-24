import streamlit as st
import pandas as pd
import time
import datetime as dt
from app.pages import report
from app.utils.caixa import salvar_dados_caixa, carregar_dados_caixa, deletar_dados_caixa, atualizar_dados_caixa
from app.utils.pagamentos import editar_pagamento, deletar_pagamento, get_pagamentos_eventos, mudar_status_pagamento_deletado

def new_record():
    st.header("Caixa Micas Daminhas")

    operacao = st.selectbox("Qual operação no caixa deseja fazer", ["Nenhum", "Relatório Financeiro", "Modificar/Deletar Pagamentos", "Adicionar Entrada/Saída", "Editar/Excluir Entradas/Saídas", "Caixa Entradas/Saídas (Sem Pagamentos)"])	

    if operacao == "Adicionar Entrada/Saída":
        with st.form(key='novo_registro_retirada_form'):
            st.markdown(f"### Novo Registro Caixa")
            data = st.date_input("Data", value=dt.date.today())
            origem = st.selectbox("Selecione a origem do valor", ["Pagamento Avulso","Devolução", "Micas", "Micas Loja", "Micas Daminhas"])
            observacao = st.text_input("Observação de Pagamento", placeholder="Observação")
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")
            operacao = st.selectbox("Operação", ["Entrada", "Saída"])	

            submit_button = st.form_submit_button(label="Salvar Registro")   

            if submit_button:
                novo_registro_retirada = {
                    "Participante_id": "Nenhum",
                    "Data": data,
                    "Origem": origem,
                    "Observação": observacao,
                    "Valor": valor,
                    "Operação": operacao	
                }
                df_novo_registro_retirada = pd.DataFrame([novo_registro_retirada])
                salvar_dados_caixa(df_novo_registro_retirada)
                st.success("Registro salvo com sucesso!")
                time.sleep(2)
                st.rerun()
    elif operacao == "Editar/Excluir Entradas/Saídas":
        st.markdown(f"### Editar/Excluir Entradas/Saídas")
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
        
    elif operacao == "Caixa Entradas/Saídas (Sem Pagamentos)":
        st.markdown(f"### Ver Caixa e Registros")
        
        registros = carregar_dados_caixa()
        filtered_registros = registros
        fallback_date = dt.date.today()
        start_date = pd.to_datetime(registros["Data"], errors="coerce").min()
        end_date = pd.to_datetime(registros["Data"], errors="coerce").max()

        opcoes_data = st.selectbox("Selecione uma opção", ["Tudo", "Datas Específicas"])
        if opcoes_data == "Datas Específicas":
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
                start_date = st.date_input("Data Inicial", value=min_date if pd.notna(start_date) else fallback_date)
                end_date = st.date_input("Data Final", value=max_date if pd.notna(end_date) else fallback_date)
            filtered_registros = registros[
                (pd.to_datetime(registros["Data"], errors="coerce") >= pd.to_datetime(start_date)) &
                (pd.to_datetime(registros["Data"], errors="coerce") <= pd.to_datetime(end_date))
            ]

        opcoes_registros = st.selectbox("Selecione uma opção", ["Todos", "Entradas", "Saídas"])
        if opcoes_registros == "Entradas":
            filtered_registros = filtered_registros[filtered_registros["Operação"] == "Entrada"]
        elif opcoes_registros == "Saídas":
            filtered_registros = filtered_registros[filtered_registros["Operação"] == "Saída"]
        
        if registros.empty:
            start_date = dt.date.today()
            end_date = dt.date.today()

        if filtered_registros.empty:
            st.warning("Nenhum registro do caixa para o período escolhido.")
        else:    
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
    elif operacao == "Modificar/Deletar Pagamentos":    
        st.markdown("### Modificar/Deletar Pagamentos")

        # Fetch payment records
        start_date = st.date_input("Data Inicial", value=dt.date.today().replace(day=1))
        end_date = st.date_input("Data Final", value=dt.date.today())
        pagamentos = get_pagamentos_eventos(start_date, end_date)

        if pagamentos.empty:
            st.warning("Nenhum pagamento encontrado no período selecionado.")
            return

        # Display payments in a data editor
        pagamentos['Deletar'] = False
        edited_df = st.data_editor(pagamentos, use_container_width=True)

        # Save changes
        if st.button("Salvar Alterações"):
            for _, row in edited_df.iterrows():
                if not row['Deletar']:
                    try:
                        editar_pagamento(
                            pagamento_id=row['id'],
                            data_pagamento=row.get('Data do Pagamento'),
                            forma_pagamento=row.get('Forma de Pagamento'),
                            taxa_maquina=row.get('Taxa da Máquina'),
                            observacao=row.get('Observação'),
                            valor_pago=row.get('Valor Pago')
                        )
                    except ValueError as e:
                        st.error(f"Erro ao editar pagamento ID {row['id']}: {e}")
            st.success("Alterações salvas com sucesso!")
            st.rerun()

        # Delete selected records
        if st.button("Deletar Registros Selecionados"):
            ids_to_delete = edited_df[edited_df['Deletar'] == True]['id'].tolist()
            if ids_to_delete:
                for pagamento_id in ids_to_delete:
                    mudar_status_pagamento_deletado(pagamento_id)
                    deletar_pagamento(pagamento_id)
                st.success("Registros deletados com sucesso!")
                st.rerun()
            else:
                st.warning("Nenhum registro selecionado para deletar.")
    else:
        st.info("Selecione uma operação para continuar.")

