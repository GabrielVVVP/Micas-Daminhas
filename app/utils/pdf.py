from fpdf import FPDF

def exportar_pagamentos_para_pdf(data_inicio, data_fim, total_valor_credito, total_valor_pago_credito, total_valor_debito, total_valor_pago_debito, total_valor_deposito, total_valor_dinheiro, total_retiradas, df_retiradas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Balanço dos Pagamentos", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Período: ({data_inicio} - {data_fim})", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Maquininha Pag Seguro Micas Virtual", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Valor Total com Taxas): R$ {total_valor_credito + total_valor_debito:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Desconto das Taxas): R$ {(total_valor_credito + total_valor_debito) - (total_valor_pago_credito + total_valor_pago_debito):.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Saldo Total sem Taxas): R$ {total_valor_pago_credito + total_valor_pago_debito:.2f}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Total", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Saldo Total sem Taxas): R$ {total_valor_pago_credito + total_valor_pago_debito:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Depósito Micas Virtual (Total): R$ {total_valor_deposito:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Dinheiro (Total): R$ {total_valor_dinheiro:.2f}", ln=True)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt=f"Saldo Total: R$ {total_valor_pago_credito + total_valor_pago_debito + total_valor_deposito + total_valor_dinheiro:.2f}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Lista de Retiradas", ln=True)
    pdf.set_font("Arial", size=12)
    for index, row in df_retiradas.iterrows():
        pdf.cell(200, 10, txt=f"Data: {row['Data']}, Valor: R$ {row['Valor']:.2f}, Observação: {row['Observação']}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Caixa Final", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Dinheiro Recebido (Total): R$ {total_valor_dinheiro:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Retiradas (Total): R$ {total_retiradas:.2f}", ln=True)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt=f"Caixa (Dinheiro Final): R$ {total_valor_dinheiro - total_retiradas:.2f}", ln=True)
    pdf.set_font("Arial", size=12)

    pdf.output(f"data/balanços/balanco_pagamentos_{data_inicio}_{data_fim}.pdf")
    return f"balanco_pagamentos_{data_inicio}_{data_fim}.pdf"

def gerar_contrato_retirada_pdf(dados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(40)
    pdf.cell(200, 10, "CONTRATO DE ALUGUEL DE ROUPA DE DAMINHA/PAJEM", ln=True, align='C')
    pdf.image("./assets/Img/Logo.jpg", x=90, y=8, w=30)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    
    # Dados do Contratante
    pdf.cell(200, 10, "1. IDENTIFICAÇÃO DAS PARTES", ln=True, align='L')
    pdf.ln(5)
    pdf.cell(200, 10, f"CONTRATANTE: {dados['contratante_nome']}", ln=True)
    pdf.cell(200, 10, f"CPF: {dados['contratante_cpf']}", ln=True)
    pdf.cell(200, 10, f"Endereço: {dados['contratante_endereco']}", ln=True)
    pdf.cell(200, 10, f"Telefone: {dados['contratante_telefone']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratante_email']}", ln=True)
    pdf.ln(5)
    
    # Dados da Contratada
    pdf.cell(200, 10, f"CONTRATADA: {dados['contratada_nome']}", ln=True)
    pdf.cell(200, 10, f"CNPJ/CPF: {dados['contratada_cnpj']}", ln=True)
    pdf.cell(200, 10, f"Endereço: {dados['contratada_endereco']}", ln=True)
    pdf.cell(200, 10, f"Telefone: {dados['contratada_telefone']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratada_email']}", ln=True)
    pdf.ln(10)
    
    # Detalhes do aluguel
    pdf.cell(200, 10, "2. DESCRIÇÃO DO SERVIÇO E ORÇAMENTO", ln=True)
    pdf.cell(200, 10, f"Modelo do item alugado: {dados['descricao_roupa']}", ln=True)
    pdf.cell(200, 10, f"Acessórios do item alugado: {dados['acessorios']}", ln=True)
    pdf.cell(200, 10, f"Observação do item alugado: {dados['obs']}", ln=True)
    pdf.cell(200, 10, f"Estado na retirada: {dados['estado_retirada']}", ln=True)
    pdf.cell(200, 10, f"Valor do aluguel: R$ {dados['valor_aluguel']}", ln=True)
    pdf.cell(200, 10, f"Data de retirada: {dados['data_retirada']}", ln=True)
    pdf.cell(200, 10, f"Data de devolução: {dados['data_devolucao']}", ln=True)
    pdf.ln(10)
    
    # Cláusulas
    pdf.multi_cell(0, 10, "3. OBRIGAÇÕES DAS PARTES\n3.1. A CONTRATADA se compromete a entregar a roupa em perfeito estado de conservação e higienizada.\n3.2. A CONTRATANTE se compromete a devolver a roupa na mesma condição em que a recebeu, sem avarias, danos, manchas ou modificações.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "4. RESPONSABILIDADE POR DANOS\n4.1. Caso a roupa seja devolvida com avarias, a CONTRATANTE será responsável pelos custos de reparo.\n4.2. Em caso de danos irreparáveis ou extravio, a CONTRATANTE deverá pagar à CONTRATADA o valor estipulado no contrato.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "5. MULTA POR ATRASO NA DEVOLUÇÃO\n5.1. O atraso na devolução da roupa acarretará multa diária conforme estipulado.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "6. DISPOSIÇÕES GERAIS\n6.1. Este contrato tem validade legal e qualquer controvérsia será resolvida no foro da comarca indicada.")
    pdf.ln(10)
    
    # Assinaturas
    pdf.cell(200, 10, "7. ASSINATURA DAS PARTES", ln=True)
    pdf.ln(20)
    pdf.cell(200, 10, "______________________________", ln=True)
    pdf.cell(200, 10, "CONTRATANTE", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "______________________________", ln=True)
    pdf.cell(200, 10, "CONTRATADA", ln=True)

    pdf.output(f"data/contratos/retirada/contrato_entrega_{dados['contratante_nome']}_{dados['data_retirada']}.pdf")
    return f"data/contratos/retirada/contrato_entrega_{dados['contratante_nome']}_{dados['data_retirada']}.pdf"

def gerar_contrato_devolucao_pdf(dados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(40)
    pdf.cell(200, 10, "CONTRATO DE DEVOLUÇÃO DE ROUPA DE DAMINHA/PAJEM", ln=True, align='C')
    pdf.image("./assets/Img/Logo.jpg", x=90, y=8, w=30)
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    # Dados do Contratante
    pdf.cell(200, 10, "1. IDENTIFICAÇÃO DAS PARTES", ln=True, align='L')
    pdf.ln(5)
    pdf.cell(200, 10, f"CONTRATANTE: {dados['contratante_nome']}", ln=True)
    pdf.cell(200, 10, f"CPF: {dados['contratante_cpf']}", ln=True)
    pdf.cell(200, 10, f"Endereço: {dados['contratante_endereco']}", ln=True)
    pdf.cell(200, 10, f"Telefone: {dados['contratante_telefone']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratante_email']}", ln=True)
    pdf.ln(5)
    
    # Dados da Contratada
    pdf.cell(200, 10, f"CONTRATADA: {dados['contratada_nome']}", ln=True)
    pdf.cell(200, 10, f"CNPJ/CPF: {dados['contratada_cnpj']}", ln=True)
    pdf.cell(200, 10, f"Endereço: {dados['contratada_endereco']}", ln=True)
    pdf.cell(200, 10, f"Telefone: {dados['contratada_telefone']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratada_email']}", ln=True)
    pdf.ln(10)
    
    # Detalhes da devolução
    pdf.cell(200, 10, "2. DESCRIÇÃO DO SERVIÇO E DEVOLUÇÃO", ln=True)
    pdf.cell(200, 10, f"Modelo do item devolvido: {dados['descricao_roupa']}", ln=True)
    pdf.cell(200, 10, f"Acessórios do item devolvido: {dados['acessorios']}", ln=True)
    pdf.cell(200, 10, f"Observação do item devolvido: {dados['obs']}", ln=True)
    pdf.cell(200, 10, f"Estado na devolução: {dados['estado_devolucao']}", ln=True)
    pdf.cell(200, 10, f"Data de devolução: {dados['data_devolucao']}", ln=True)
    pdf.ln(10)
    
    # Cláusulas
    pdf.multi_cell(0, 10, "3. OBRIGAÇÕES DAS PARTES\n3.1. A CONTRATADA se compromete a verificar o estado da roupa devolvida e informar qualquer irregularidade.\n3.2. A CONTRATANTE se compromete a devolver a roupa na mesma condição em que a recebeu, sem avarias, danos, manchas ou modificações.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "4. RESPONSABILIDADE POR DANOS\n4.1. Caso a roupa seja devolvida com avarias, a CONTRATANTE será responsável pelos custos de reparo.\n4.2. Em caso de danos irreparáveis ou extravio, a CONTRATANTE deverá pagar à CONTRATADA o valor estipulado no contrato.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "5. MULTA POR ATRASO NA DEVOLUÇÃO\n5.1. O atraso na devolução da roupa acarretará multa diária conforme estipulado.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "6. DISPOSIÇÕES GERAIS\n6.1. Este contrato tem validade legal e qualquer controvérsia será resolvida no foro da comarca indicada.")
    pdf.ln(10)
    
    # Assinaturas
    pdf.cell(200, 10, "7. ASSINATURA DAS PARTES", ln=True)
    pdf.ln(20)
    pdf.cell(200, 10, "______________________________", ln=True)
    pdf.cell(200, 10, "CONTRATANTE", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "______________________________", ln=True)
    pdf.cell(200, 10, "CONTRATADA", ln=True)

    pdf.output(f"data/contratos/devolucao/contrato_devolucao_{dados['contratante_nome']}_{dados['data_devolucao']}.pdf")
    return f"data/contratos/devolucao/contrato_devolucao_{dados['contratante_nome']}_{dados['data_devolucao']}.pdf"