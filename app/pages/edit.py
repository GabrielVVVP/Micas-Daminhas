import streamlit as st
from app.pages import init_processes, clients, budget, contracts, participants, payment

def edit_record():
    st.header("Funil de Registros")

    options_clients = st.selectbox(
        "Selecione o tipo de registro que deseja editar:",
        ("Início","Eventos", "Participantes", "Medidas e Orçamentos", "Contratos", "Pagamentos")	
    )
    if options_clients == "Início":
        init_processes.init_processes()
    elif options_clients == "Eventos":
        clients.new_record()
    elif options_clients == "Participantes":
        participants.new_record()
    elif options_clients == "Medidas e Orçamentos":
        budget.budget()
    elif options_clients == "Contratos":
        contracts.contracts() 
    elif options_clients == "Pagamentos":
        payment.payment()              
    else:
        st.warning("Selecione uma opção.")    