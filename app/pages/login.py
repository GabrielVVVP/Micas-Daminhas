import streamlit as st
from app.utils.users import authenticate_user, send_reset_email, is_only_admin_user

def login():
    st.sidebar.title("Sistema - Micas Daminhas")
    menu = ["Início","Login"]
    choice = st.sidebar.selectbox("Menu", menu)

    if "page" not in st.session_state:
        st.session_state["page"] = "Login"

    if choice == "Login":
        if st.session_state.page == "forgot_password":
            st.title("Recuperação de Senha")
            email = st.text_input("Email da conta")
            new_password = st.text_input("Nova senha", type="password")
            confirm_password = st.text_input("Confirme a nova senha", type="password")
            master_key = st.text_input("Chave Mestre")

            if st.button("Alterar Senha"):
                if not email or not new_password or not confirm_password or not master_key:
                    st.warning("Por favor, preencha todos os campos.")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem.")
                elif master_key != "Micas@SenhaMestre":
                    st.error("Chave Mestre inválida.")
                else:
                    # Aqui você pode adicionar a lógica para alterar a senha no banco de dados
                    st.success("Senha alterada com sucesso! Faça login com sua nova senha.")
                    st.session_state.page = "Login"
                    st.rerun()

            if st.button("Voltar"):
                st.session_state.page = "Login"
                st.rerun()
        else:
            st.title("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user = authenticate_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_name = user[1]
                    st.session_state.user_type = user[2]
                    st.session_state.user_email = email
                    st.session_state.user_password = password
                    st.success(f"Bem vinda {user[1]}!")
                    st.rerun()
                else:
                    st.error("Dados inválidos")
            
            if st.button("Esqueceu a senha?"):
                st.session_state.page = "forgot_password"
                st.rerun()

            if is_only_admin_user():
                st.info("Bem vindo ao sistema! A conta padrão é email: admin@micas.com.br e a senha: 123456.")
                st.info("Após o seu primeiro acesso, modifique a senha padrão desta conta e depois crie um novo usuário de vendas.")
                st.info("Uma vez que a segunda conta for criada, esta mensagem padrão irá desaparecer.")
    else: 
        colm1, colm2, colm3 = st.columns([2, 4, 1])
        with colm2:
            st.title("Sistema - Micas Daminhas")
            st.write("Bem-vindo ao sistema da Micas Daminhas!")
            st.write("Realize o seu login para começar.")
            st.write("")
            st.write("")
            st.write("")
            st.write("Desenvolvido por Gabriel Vilaça. Direitos Reservados © 2025")

