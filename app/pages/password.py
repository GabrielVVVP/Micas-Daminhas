import streamlit as st
from app.utils.users import user_exists, get_user_id_by_email, update_user_password

def reset_password():
    st.title("Reset Password")
    email = st.text_input("Email")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Reset Password"):
        if not email or not new_password or not confirm_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif not user_exists(email):
            st.error("No account found with this email.")
        else:
            # Update the user's password
            with st.spinner("Updating password..."):
                user_id = get_user_id_by_email(email) 
                update_user_password(user_id, new_password)
                st.success("Your password has been reset successfully. You can now log in.")
