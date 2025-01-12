import pyAesCrypt
import secrets
import streamlit as st
import os
import tempfile
from pymongo import MongoClient

username="andyduoduo8@gmail.com"
password="u5GP4TV#yutiAnD"
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

MONGO_URI = "mongodb+srv://{escaped_username}:{escaped_password}@cluster22207.vyuec.mongodb.net/?retryWrites=true&w=majority&appName=Cluster22207"
client = MongoClient(MONGO_URI)
db = client.Encryption
mycol = db.Keys
BUFFER_SIZE = 64 * 1024

def encrypt_file(uploaded_file, name, mycol):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_input_path = os.path.join(temp_dir, "temp_input_file")
        temp_encrypted_path = os.path.join(temp_dir, "temp_encrypted_file.aes")

        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.read())

        password = secrets.token_urlsafe(20)
        myquery = {"name": name}
        result = mycol.find_one(myquery)
        if result:
            st.success(f"Key already exists for {name}: {result['key']}")
            pyAesCrypt.encryptFile(temp_input_path, temp_encrypted_path, result['key'], BUFFER_SIZE)
        else:
            mycol.insert_one({"name": name, "key": password})
            st.success(f"Your encryption key is: {password}")
            pyAesCrypt.encryptFile(temp_input_path, temp_encrypted_path, password, BUFFER_SIZE)

        with open(temp_encrypted_path, "rb") as f:
            st.download_button(
                label="Download Encrypted File",
                data=f.read(),
                file_name="encrypted_file.aes",
                mime="application/octet-stream",
            )

def decrypt_file(uploaded_file, name, mycol, file_extension):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_input_path = os.path.join(temp_dir, "temp_input_file")
        temp_decrypted_path = os.path.join(temp_dir, f"temp_decrypted_file.{file_extension}")

        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.read())

        myquery = {"name": name}
        result = mycol.find_one(myquery)
        if result:
            password = result["key"]
            try:
                pyAesCrypt.decryptFile(temp_input_path, temp_decrypted_path, password, BUFFER_SIZE)
                with open(temp_decrypted_path, "rb") as f:
                    mime_type = {
                        "pdf": "application/pdf",
                        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "txt": "text/plain",
                        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    }[file_extension]

                    st.download_button(
                        label="Download Decrypted File",
                        data=f.read(),
                        file_name=f"decrypted_file.{file_extension}",
                        mime=mime_type,
                    )
            except ValueError:
                st.error("Decryption failed: Wrong password or file is corrupted.")
                st.error(f"Stored Password: {password}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.error("No matching key found for the given name.")

def main():
    st.title("Encryption Tool")
    name = st.text_input("Enter Your Name:")
    if not name:
        st.warning("Please enter your name to proceed.")
        return

    choice = st.selectbox("Select an Action:", ("1: Encrypt", "2: Decrypt"))
    uploaded_file = st.file_uploader("Choose a File:")

    if uploaded_file:
        if choice.startswith("1"):
            encrypt_file(uploaded_file, name, mycol)
        elif choice.startswith("2"):
            file_type = st.selectbox(
                "Select File Type of Original File:",
                ("1: PDF", "2: DOCX", "3: TXT", "4: PPTX"),
            )
            extensions = {"1": "pdf", "2": "docx", "3": "txt", "4": "pptx"}
            decrypt_file(uploaded_file, name, mycol, extensions[file_type[0]])

if __name__ == "__main__":
    main()
