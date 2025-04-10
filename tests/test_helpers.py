import unittest
import os
import pandas as pd
from app.utils.helpers import (
    initialize_database,
    create_user,
    user_exists,
    authenticate_user,
    salvar_dados_pagamentos,
    deletar_dados,
    salvar_dados_participantes,
    atualizar_dados_participantes,
    deletar_dados_participantes,
    get_db_connection
)

class TestHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure the database is initialized before running tests
        initialize_database()

    def setUp(self):
        # Clear the database before each test
        with get_db_connection() as conn:
            conn.execute("DELETE FROM users")
            conn.execute("DELETE FROM pagamentos")
            conn.execute("DELETE FROM participantes")

    def test_create_user(self):
        create_user("Test User", "test@example.com", "User", "password123")
        self.assertTrue(user_exists("test@example.com"))

    def test_authenticate_user(self):
        create_user("Test User", "test@example.com", "User", "password123")
        user = authenticate_user("test@example.com", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "Test User")

    def test_salvar_dados_pagamentos(self):
        df = pd.DataFrame([{
            "Data": "2023-10-01",
            "Noiva": "Maria",
            "Data do Casamento": "2023-12-01",
            "Valor": 1000.0,
            "Forma de Pagamento": "Cartão",
            "Observação": "Nenhuma",
            "Auto": "Sim",
            "Taxa de Desconto": 0.0,
            "Valor Pago": 1000.0,
            "Status": "Pago"
        }])
        salvar_dados_pagamentos(df)
        with get_db_connection() as conn:
            result = conn.execute("SELECT * FROM pagamentos").fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][2], "Maria")  # Check "Noiva" column

    def test_deletar_dados_pagamentos(self):
        df = pd.DataFrame([{
            "Data": "2023-10-01",
            "Noiva": "Maria",
            "Data do Casamento": "2023-12-01",
            "Valor": 1000.0,
            "Forma de Pagamento": "Cartão",
            "Observação": "Nenhuma",
            "Auto": "Sim",
            "Taxa de Desconto": 0.0,
            "Valor Pago": 1000.0,
            "Status": "Pago"
        }])
        salvar_dados_pagamentos(df)
        with get_db_connection() as conn:
            ids = [row[0] for row in conn.execute("SELECT id FROM pagamentos").fetchall()]
        deletar_dados(ids)
        with get_db_connection() as conn:
            result = conn.execute("SELECT * FROM pagamentos").fetchall()
        self.assertEqual(len(result), 0)

    def test_salvar_dados_participantes(self):
        df = pd.DataFrame([{
            "Evento_id": 1,
            "Data": "2023-10-01",
            "Responsável Financeiro": "João",
            "Nome": "Ana",
            "Tipo": "Daminha",
            "Telefone": "123456789",
            "Email": "ana@example.com",
            "Endereço": "Rua A",
            "CPF": "123.456.789-00",
            "Status": "Ativo"
        }])
        salvar_dados_participantes(df)
        with get_db_connection() as conn:
            result = conn.execute("SELECT * FROM participantes").fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][4], "Ana")  # Check "Nome" column

    def test_atualizar_dados_participantes(self):
        df = pd.DataFrame([{
            "Evento_id": 1,
            "Data": "2023-10-01",
            "Responsável Financeiro": "João",
            "Nome": "Ana",
            "Tipo": "Daminha",
            "Telefone": "123456789",
            "Email": "ana@example.com",
            "Endereço": "Rua A",
            "CPF": "123.456.789-00",
            "Status": "Ativo"
        }])
        salvar_dados_participantes(df)
        # Update the data
        with get_db_connection() as conn:
            participante_id = conn.execute("SELECT id FROM participantes WHERE Nome = 'Ana'").fetchone()[0]
        updated_df = pd.DataFrame([{
            "id": participante_id,
            "Evento_id": 1,
            "Responsável Financeiro": "João",
            "Nome": "Ana Maria",  # Updated name
            "Tipo": "Daminha",
            "Telefone": "987654321",  # Updated phone
            "Email": "ana@example.com",
            "Endereço": "Rua A",
            "CPF": "123.456.789-00",
            "Status": "Atualizado"
        }])
        atualizar_dados_participantes(updated_df)
        with get_db_connection() as conn:
            result = conn.execute("SELECT * FROM participantes").fetchall()
        self.assertEqual(result[0][4], "Ana Maria")  # Check updated "Nome"
        self.assertEqual(result[0][6], "987654321")  # Check updated "Telefone"

    def test_deletar_dados_participantes(self):
        df = pd.DataFrame([{
            "Evento_id": 1,
            "Data": "2023-10-01",
            "Responsável Financeiro": "João",
            "Nome": "Ana",
            "Tipo": "Daminha",
            "Telefone": "123456789",
            "Email": "ana@example.com",
            "Endereço": "Rua A",
            "CPF": "123.456.789-00",
            "Status": "Ativo"
        }])
        salvar_dados_participantes(df)
        with get_db_connection() as conn:
            ids = [row[0] for row in conn.execute("SELECT id FROM participantes").fetchall()]
        deletar_dados_participantes(ids)
        with get_db_connection() as conn:
            result = conn.execute("SELECT * FROM participantes").fetchall()
        self.assertEqual(len(result), 0)

if __name__ == "__main__":
    unittest.main()
