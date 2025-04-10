import random
import smtplib
import re
from email.mime.text import MIMEText
from app.utils.helpers import get_db_connection, hash_password

# Users

def unique_key():
    return random.randint(0, 199999)

def get_user_info(user_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT Nome, Email, Account_Type FROM users WHERE id = ?", (user_id,))
        user_info = c.fetchone()
        if user_info:
            return {
                "name": user_info[0],
                "email": user_info[1],
                "type": user_info[2]
            }
        return None

def user_exists(email):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE Email = ?", (email,))
        return c.fetchone() is not None

def authenticate_user(email, password):   
    hashed_password = hash_password(password)
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, Nome, Account_Type FROM users WHERE Email = ? AND Password = ?", (email, hashed_password))
        return c.fetchone()

def create_user(name, email, account_type, password):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users (Nome, Email, Account_Type, Password) VALUES (?, ?, ?, ?)", (name, email, account_type, hash_password(password)))
        conn.commit()

def update_user(user_id, name, email, account_type):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET Nome = ?, Email = ?, Account_Type = ? WHERE id = ?", (name, email, account_type, user_id))
        conn.commit()

def update_user_password(user_id, password):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET Password = ? WHERE id = ?", (hash_password(password), user_id))
        conn.commit()

def delete_user(user_id):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

def send_reset_email(email):
    try:
        # Define email content
        reset_link = f"http://example.com/reset-password?email={email}"  # Replace with actual reset link
        msg = MIMEText(f"Click the link to reset your password: {reset_link}")
        msg['Subject'] = "Password Reset Request"
        msg['From'] = "no-reply@micasdaminhas.com"
        msg['To'] = email

        # Send email
        with smtplib.SMTP('smtp.example.com', 587) as server:  # Replace with actual SMTP server
            server.starttls()
            server.login("your_email@example.com", "your_password")  # Replace with actual credentials
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def get_user_id_by_email(email):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE Email = ?", (email,))
        result = c.fetchone()
        return result[0] if result else None

def is_only_admin_user():
    """
    Check if the users table only contains the Admin user.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        return user_count == 1  # True if only one user exists (Admin)    