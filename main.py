import streamlit as st
from streamlit_option_menu import option_menu
from app.pages import clients, home, participants, login, profile, register, payment, edit, report, funnel, budget, contracts
from app.utils.helpers import initialize_database  

# Database setup
initialize_database() 

# Streamlit App
st.set_page_config(page_title="Sistema de Pagamento - Micas Daminhas", page_icon="assets/Img/Logo.jpg", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_type = None

# Interface Streamlit
col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    st.image("assets/Img/Logo.jpg", use_container_width=True)

# Logout button
def logoutButton():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_type = None
        st.rerun()     

def main():

    if not st.session_state.logged_in:
        login.login()
    else:
        if st.session_state.user_type == "Vendas":
            st.sidebar.title("Vendas - Micas Daminhas")
            st.sidebar.write("Bem vinda " + st.session_state.user_name + "!")
            with st.sidebar:
                menu = option_menu("Menu Principal", ["Tela Inicial","Cadastro Clientes","Cadastro Participantes", "Orçamento e Medidas", "Pagamentos e Contratos","Funil de Processos","Perfil"], 
                    icons=['house', 'building-fill-add','person-plus', 'pencil','cash','funnel','person'], menu_icon="cast", default_index=0)
            logoutButton()
            if menu == "Tela Inicial":
                home.home() 
            elif menu == "Cadastro Clientes":
                clients.new_record()
            elif menu == "Cadastro Participantes":
                participants.new_record()  
            elif menu == "Orçamento e Medidas":
                budget.budget() 
            elif menu == "Pagamentos e Contratos":
                payment.payment()                 
            elif menu == "Funil de Processos":
                funnel.funnel_report()
            elif menu == "Perfil":
                profile.profile()      
        else:
            st.sidebar.title("Admin - Micas Daminhas")
            st.sidebar.write("Bem vinda " + st.session_state.user_name + "!")
            with st.sidebar:
                menu = option_menu("Menu Principal", ["Tela Inicial","Novos Registros","Relatório de Clientes","Financeiro Micas Daminhas", "Perfil"], 
                    icons=['house', 'cash','book', 'pencil-square','person'], menu_icon="cast", default_index=0)
            logoutButton()
            if menu == "Tela Inicial":
                home.home()  
            elif menu == "Novos Registros":
                edit.edit_record()       
            elif menu == "Relatório de Clientes":
                funnel.funnel_report()    
            elif menu == "Financeiro Micas Daminhas":
                register.new_record()   
            elif menu == "Perfil":
                profile.profile()   

if __name__ == "__main__":
    main()

