import datetime as dt
from fpdf import FPDF
from app.utils.helpers import ensure_month_year_folder, convert_date_format


def exportar_pagamentos_para_pdf(data_inicio, data_fim, total_valor_credito, total_valor_pago_credito, total_valor_debito, total_valor_pago_debito, total_valor_deposito, total_valor_dinheiro, total_retiradas, df_retiradas, total_entradas, df_entradas):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Balanço dos Pagamentos", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Período: ({convert_date_format(str(data_inicio))} - {convert_date_format(str(data_fim))})", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Maquininha Pag Seguro Micas Virtual", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Valor Total com Taxas): R$ {total_valor_credito + total_valor_debito:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Desconto das Taxas): R$ {(total_valor_credito + total_valor_debito) - (total_valor_pago_credito + total_valor_pago_debito):.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Saldo Total sem Taxas): R$ {total_valor_pago_credito + total_valor_pago_debito:.2f}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Total", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Maquininha Pag Seguro Micas Virtual (Saldo Total sem Taxas): R$ {total_valor_pago_credito + total_valor_pago_debito:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Depósito Micas Virtual (Total): R$ {total_valor_deposito:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Dinheiro (Total): R$ {total_valor_dinheiro:.2f}", ln=True)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt=f"Saldo Total: R$ {total_valor_pago_credito + total_valor_pago_debito + total_valor_deposito + total_valor_dinheiro:.2f}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Lista de Entradas (Avulsas)", ln=True)
    pdf.set_font("Arial", size=10)
    for index, row in df_entradas.iterrows():
        pdf.cell(200, 10, txt=f"Data: {row['Data']}, Valor: R$ {row['Valor']:.2f}, Observação: {row['Observação']}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Lista de Retiradas", ln=True)
    pdf.set_font("Arial", size=10)
    for index, row in df_retiradas.iterrows():
        pdf.cell(200, 10, txt=f"Data: {row['Data']}, Valor: R$ {row['Valor']:.2f}, Observação: {row['Observação']}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Caixa Final", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Dinheiro Recebido (Total): R$ {total_valor_pago_credito + total_valor_pago_debito + total_valor_deposito + total_valor_dinheiro:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Entradas Avulsas (Total): R$ {total_entradas:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Retiradas (Total): R$ {total_retiradas:.2f}", ln=True)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt=f"Caixa (Dinheiro Final): R$ {total_valor_pago_credito + total_valor_pago_debito + total_valor_deposito + total_valor_dinheiro + total_entradas - total_retiradas:.2f}", ln=True)
    pdf.set_font("Arial", size=10)

    origin_path = "data/resumo_de_faturamento/"
    base_path = ensure_month_year_folder(origin_path,data_fim)
    file_path = f"/balanco_pagamentos_{data_inicio}_{data_fim}.pdf"
    pdf.output(base_path+file_path)
    return base_path,file_path

def exportar_producao_para_pdf(orcamento_meninas, orcamento_meninos, nome):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt=f"Produção de Roupas de Daminhas e Pajens - Cliente {nome}", ln=True, align='C')
    pdf.ln(10)
    
    # Dados de orcamento_meninas
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Vestidos - Meninas", ln=True)
    pdf.set_font("Arial", size=12)
    for index, row in orcamento_meninas.iterrows():
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(0, 10, txt="Participante "+str(index+1), ln=True)
        pdf.set_font("Arial", size=8)
        pdf.multi_cell(0, 10, txt=(
            f"Data: {convert_date_format(str(row['Data']))}\n"
            f"Nome da Cliente: {nome}\n"
            f"Nome do Participante: {row['Nome do Participante']}\n"
            f"Busto: {row['Busto']} cm\n"
            f"Cintura: {row['Cintura']} cm\n"
            f"Ombro-Cintura: {row['Ombro-Cintura']} cm\n"
            f"Cintura-Pé: {row['Cintura-Pé']} cm\n"
            f"Modelo: {row['Modelo']}\n"
            f"Acessórios: {row['Acessórios']}\n"
            f"Observação: {row['Observação']}\n"
        ))
        pdf.ln(5)
    
    pdf.ln(10)
    
    # Dados de orcamento_meninos
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Trajes - Meninos", ln=True)
    pdf.set_font("Arial", size=12)
    for index, row in orcamento_meninos.iterrows():
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(0, 10, txt="Participante "+str(index+1), ln=True)
        pdf.set_font("Arial", size=8)
        pdf.multi_cell(0, 10, txt=(
            f"Data: {row['Data']}\n"
            f"Nome da Cliente: {nome}\n"
            f"Nome do Participante: {row['Nome do Participante']}\n"
            f"Ombro-Punho: {row['Ombro-Punho']} cm\n"
            f"Bainha-Calça: {row['Bainha-Calça']} cm\n"
            f"Modelo: {row['Modelo']}\n"
            f"Acessórios: {row['Acessórios']}\n"
            f"Observação: {row['Observação']}\n"
        ))
        pdf.ln(5)
    
    pdf.ln(10)
    
    origin_path = "data/producao_medidas/"
    base_path = ensure_month_year_folder(origin_path,dt.datetime.today())
    file_path = f"/producao_{nome}_{dt.datetime.today().strftime('%Y-%m-%d')}.pdf"
    pdf.output(base_path+file_path)
    return base_path,file_path

def gerar_contrato_retirada_pdf(dados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(40)
    pdf.cell(200, 10, "CONTRATO DE ALUGUEL DE ROUPA DE DAMINHA/PAJEM", ln=True, align='C')
    pdf.image("./assets/Img/Logo.jpg", x=90, y=8, w=30)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    
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
    pdf.cell(200, 10, f"Whatsapp: {dados['contratada_whatsapp']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratada_email']}", ln=True)
    pdf.ln(10)
    
    # Detalhes do aluguel
    pdf.cell(200, 10, "2. DESCRIÇÃO DO SERVIÇO E ORÇAMENTO", ln=True)
    pdf.cell(200, 10, f"Modelo do item alugado: {dados['descricao_roupa']}", ln=True)
    pdf.cell(200, 10, f"Acessórios do item alugado: {dados['acessorios']}", ln=True)
    pdf.cell(200, 10, f"Observação do item alugado: {dados['obs']}", ln=True)
    pdf.cell(200, 10, f"Estado na retirada: {dados['estado_retirada']}", ln=True)
    pdf.cell(200, 10, f"Valor do aluguel: R$ {dados['valor_aluguel']}", ln=True)
    pdf.cell(200, 10, f"Desconto: R$ {dados['valor_desc']:.2f}", ln=True)
    pdf.cell(200, 10, f"Valor Total com Desconto: R$ {dados['valor_aluguel_desc']:.2f}", ln=True)
    pdf.cell(200, 10, f"Data de retirada: {convert_date_format(str(dados['data_retirada']))}", ln=True)
    pdf.cell(200, 10, f"Data de devolução: {convert_date_format(str(dados['data_devolucao']))}", ln=True)
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

    data_retirada = dt.datetime.strptime(dados['data_retirada'], "%Y-%m-%d")

    origin_path = "data/contratos/retirada/"
    base_path = ensure_month_year_folder(origin_path,data_retirada)
    file_path = f"/contrato_entrega_{dados['contratante_nome']}_{dados['participante_nome']}_{data_retirada.strftime("%d-%m-%Y")}.pdf"
    pdf_path = base_path+file_path
    pdf.output(pdf_path)
    return pdf_path

def gerar_contrato_retirada_todos_pdf(dados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(40)
    pdf.cell(200, 10, "CONTRATO DE ALUGUEL DE ROUPAS DE DAMINHAS/PAJENS", ln=True, align='C')
    pdf.image("./assets/Img/Logo.jpg", x=90, y=8, w=30)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    
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
    pdf.cell(200, 10, f"Whatsapp: {dados['contratada_whatsapp']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratada_email']}", ln=True)
    pdf.ln(10)
    
    # Detalhes do aluguel
    pdf.cell(200, 10, "2. DESCRIÇÃO DOS SERVIÇOS E ORÇAMENTO", ln=True)
    total_valor_aluguel = 0
    total_desc_aluguel = 0
    total_valor_desc_aluguel = 0
    for i in range(len(dados["descricao_roupa"])):
        pdf.cell(200, 10, f"Modelo do item alugado: {dados['descricao_roupa'][i]}", ln=True)
        pdf.cell(200, 10, f"Acessórios do item alugado: {dados['acessorios'][i]}", ln=True)
        pdf.cell(200, 10, f"Observação do item alugado: {dados['obs'][i]}", ln=True)
        pdf.cell(200, 10, f"Estado na retirada: {dados['estado_retirada'][i]}", ln=True)
        pdf.cell(200, 10, f"Valor do aluguel: R$ {dados['valor_aluguel'][i]:.2f}", ln=True)
        pdf.cell(200, 10, f"Desconto: R$ {dados['valor_desc'][i]:.2f}", ln=True)
        pdf.cell(200, 10, f"Valor Total com Desconto: R$ {dados['valor_aluguel_desc'][i]:.2f}", ln=True)
        pdf.cell(200, 10, f"Data de retirada: {convert_date_format(str(dados['data_retirada'][i]))}", ln=True)
        pdf.cell(200, 10, f"Data de devolução: {convert_date_format(str(dados['data_devolucao'][i]))}", ln=True)
        pdf.ln(5)
        total_valor_aluguel += dados['valor_aluguel'][i]
        total_desc_aluguel += dados['valor_desc'][i]
        total_valor_desc_aluguel += dados['valor_aluguel_desc'][i]
    
    pdf.ln(5)
    pdf.cell(200, 10, f"Valor Total do Aluguel: R$ {total_valor_aluguel:.2f}", ln=True)
    pdf.cell(200, 10, f"Valor Total dos Descontos: R$ {total_desc_aluguel:.2f}", ln=True)
    pdf.cell(200, 10, f"Valor Total com Descontos: R$ {total_valor_desc_aluguel:.2f}", ln=True)
    pdf.ln(10)
    
    # Cláusulas
    pdf.multi_cell(0, 10, "3. OBRIGAÇÕES DAS PARTES\n3.1. A CONTRATADA se compromete a entregar as roupas em perfeito estado de conservação e higienizadas.\n3.2. A CONTRATANTE se compromete a devolver as roupas na mesma condição em que as recebeu, sem avarias, danos, manchas ou modificações.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "4. RESPONSABILIDADE POR DANOS\n4.1. Caso as roupas sejam devolvidas com avarias, a CONTRATANTE será responsável pelos custos de reparo.\n4.2. Em caso de danos irreparáveis ou extravio, a CONTRATANTE deverá pagar à CONTRATADA o valor estipulado no contrato.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "5. MULTA POR ATRASO NA DEVOLUÇÃO\n5.1. O atraso na devolução das roupas acarretará multa diária conforme estipulado.")
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

    data_hoje = dt.datetime.today()

    origin_path = "data/contratos/retirada/"
    base_path = ensure_month_year_folder(origin_path,data_hoje)
    file_path = f"/contrato_entrega_todos_{dados['contratante_nome']}_{data_hoje.strftime("%d-%m-%Y")}.pdf"
    pdf_path = base_path+file_path
    pdf.output(pdf_path)
    return pdf_path

def gerar_contrato_devolucao_pdf(dados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(40)
    pdf.cell(200, 10, "CONTRATO DE DEVOLUÇÃO DE ROUPA DE DAMINHA/PAJEM", ln=True, align='C')
    pdf.image("./assets/Img/Logo.jpg", x=90, y=8, w=30)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
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
    pdf.cell(200, 10, f"Whatsapp: {dados['contratada_whatsapp']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratada_email']}", ln=True)
    pdf.ln(10)
    
    # Detalhes da devolução
    pdf.cell(200, 10, "2. DESCRIÇÃO DO SERVIÇO E DEVOLUÇÃO", ln=True)
    pdf.cell(200, 10, f"Modelo do item devolvido: {dados['descricao_roupa']}", ln=True)
    pdf.cell(200, 10, f"Acessórios do item devolvido: {dados['acessorios']}", ln=True)
    pdf.cell(200, 10, f"Observação do item devolvido: {dados['obs']}", ln=True)
    pdf.cell(200, 10, f"Estado na devolução: {dados['estado_devolucao']}", ln=True)
    pdf.cell(200, 10, f"Data de devolução: {convert_date_format(str(dados['data_devolucao']))}", ln=True)
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

    data_devolucao = dt.datetime.strptime(dados['data_devolucao'], "%Y-%m-%d")

    origin_path = "data/contratos/devolucao/"
    base_path = ensure_month_year_folder(origin_path,data_devolucao)
    file_path = f"/contrato_devolucao_{dados['contratante_nome']}_{dados['participante_nome']}_{data_devolucao.strftime("%d-%m-%Y")}.pdf"
    pdf_path = base_path+file_path
    pdf.output(pdf_path)
    return pdf_path

def gerar_contrato_devolucao_todos_pdf(dados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.ln(40)
    pdf.cell(200, 10, "CONTRATO DE DEVOLUÇÃO DE ROUPAS DE DAMINHAS/PAJENS", ln=True, align='C')
    pdf.image("./assets/Img/Logo.jpg", x=90, y=8, w=30)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
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
    pdf.cell(200, 10, f"Whatsapp: {dados['contratada_whatsapp']}", ln=True)
    pdf.cell(200, 10, f"E-mail: {dados['contratada_email']}", ln=True)
    pdf.ln(10)
    
    # Detalhes da devolução
    pdf.cell(200, 10, "2. DESCRIÇÃO DOS SERVIÇOS E DEVOLUÇÃO", ln=True)
    total_valor_aluguel = 0
    for i in range(len(dados["descricao_roupa"])):
        pdf.cell(200, 10, f"Modelo do item devolvido: {dados['descricao_roupa'][i]}", ln=True)
        pdf.cell(200, 10, f"Acessórios do item devolvido: {dados['acessorios'][i]}", ln=True)
        pdf.cell(200, 10, f"Observação do item devolvido: {dados['obs'][i]}", ln=True)
        pdf.cell(200, 10, f"Estado na devolução: {dados['estado_devolucao'][i]}", ln=True)
        pdf.cell(200, 10, f"Data de devolução: {convert_date_format(str(dados['data_devolucao'][i]))}", ln=True)
        pdf.ln(5)
    
    pdf.ln(10)
    
    # Cláusulas
    pdf.multi_cell(0, 10, "3. OBRIGAÇÕES DAS PARTES\n3.1. A CONTRATADA se compromete a verificar o estado das roupas devolvidas e informar qualquer irregularidade.\n3.2. A CONTRATANTE se compromete a devolver as roupas na mesma condição em que as recebeu, sem avarias, danos, manchas ou modificações.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "4. RESPONSABILIDADE POR DANOS\n4.1. Caso as roupas sejam devolvidas com avarias, a CONTRATANTE será responsável pelos custos de reparo.\n4.2. Em caso de danos irreparáveis ou extravio, a CONTRATANTE deverá pagar à CONTRATADA o valor estipulado no contrato.")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "5. MULTA POR ATRASO NA DEVOLUÇÃO\n5.1. O atraso na devolução das roupas acarretará multa diária conforme estipulado.")
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

    data_hoje = dt.datetime.today()

    origin_path = "data/contratos/devolucao/"
    base_path = ensure_month_year_folder(origin_path,data_hoje)
    file_path = f"/contrato_devolucao_todos_{dados['contratante_nome']}_{data_hoje.strftime("%d-%m-%Y")}.pdf"
    pdf_path = base_path+file_path
    pdf.output(pdf_path)
    return pdf_path
