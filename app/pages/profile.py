import streamlit as st
import time
from app.pages import signup, mstr_key
from app.utils.helpers import is_valid_email, is_valid_password
from app.utils.users import get_user_info, update_user, update_user_password  # Assuming these functions exist

def profile():
    user_info = get_user_info(st.session_state.user_id)  
    options_profile = "Perfil"

    if user_info["type"] == "Admin":
        options_profile = st.selectbox(
        "Selecione o que deseja fazer na sua conta:",
        ("Perfil","Editar Perfil","Alterar Senha","Criar Nova Conta","Modificar a Chave Mestre")
        )
    if options_profile == "Editar Perfil":
        with st.container(border=True):
            st.write("Alterar Informações de Conta")
            new_name = st.text_input("Novo Nome", value=user_info["name"])
            new_email = st.text_input("Novo Email", value=user_info["email"])
            if st.button("Atualizar Informações"):
                if not is_valid_email(new_email):
                    st.error("Por favor, insira um email válido.")
                else:    
                    update_user(st.session_state.user_id, new_name, new_email, user_info["type"])
                    st.success("Informações atualizadas com sucesso!")
                    time.sleep(2)
                    st.rerun()
    elif options_profile == "Alterar Senha":
        with st.container(border=True):
            st.write("Alterar Senha")
            new_password = st.text_input("Nova Senha", type="password")
            confirm_password = st.text_input("Confirmar Senha", type="password")
            if st.button("Alterar Senha"):
                if new_password == confirm_password:
                    if not is_valid_password(confirm_password):
                        st.error("A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, uma letra minúscula e um número.")
                    else:
                        update_user_password(st.session_state.user_id, new_password)
                        st.success("Senha alterada com sucesso!")
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("As senhas não coincidem. Tente novamente.")            
    elif options_profile == "Criar Nova Conta":
        with st.container(border=True):
            signup.signup()
    elif options_profile == "Modificar a Chave Mestre":
        with st.container(border=True):
            mstr_key.change_master_key()
    else:
        with st.container(border=True):
            st.title("Perfil - Micas Daminhas")

            st.write("Nome: " + user_info["name"])
            st.write("Email: " + user_info["email"])
            st.write("Tipo de Conta: " + user_info["type"])
            
            show_permissions = st.checkbox("Mostrar Permissões de Acesso", value=True)

        if show_permissions:
            with st.container(border=True):
                st.subheader("Permissões de Acesso")
                st.write("Você possui as seguintes permissões de acesso:")
                if user_info["type"] == "Vendas":
                    st.write("Permissões: Vendas")
                    st.write("Criar e Editar Clientes e Participantes")
                    st.write("Criar e Editar Orçamentos")
                    st.write("Criar e Editar Retirada e Devolução")
                    st.write("Você não tem permissão para criar novas contas.")
                else:
                    st.write("Permissões: Admin")
                    st.write("Criar e Editar Clientes e Participantes")
                    st.write("Criar e Editar Orçamentos")
                    st.write("Criar e Editar Retirada e Devolução")
                    st.write("Criar e Editar Relatórios")
                    st.write("Criar e Editar Contas de Usuários")
                    st.write("Upload de Arquivos")

