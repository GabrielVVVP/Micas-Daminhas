import streamlit as st
from app.pages import clients, budget, contracts, participants, payment

def edit_record():
    st.header("Criar/Editar Clientes, Participantes, Orçamentos, Pagamentos e Contratos")

    options_clients = st.selectbox(
        "Selecione o tipo de registro que deseja editar:",
        ("Nenhum","Clientes", "Participantes", "Orçamentos", "Pagamentos e Contratos")	
    )

    if options_clients == "Clientes":
        clients.new_record()
    elif options_clients == "Participantes":
        participants.new_record()
    elif options_clients == "Orçamentos":
        budget.budget()
    elif options_clients == "Pagamentos e Contratos":
        payment.payment()              
    else:
        st.warning("Selecione uma opção.")    