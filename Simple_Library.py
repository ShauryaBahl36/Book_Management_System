import mysql.connector
import streamlit as st

# Database connection setup and creation of database and table
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="Kukullaa@1024"  # Replace with your MySQL password
    )
    cursor = connection.cursor()

    # Step 1: Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS book_management")
    connection.close()

    # Step 2: Connect to the created database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kukullaa@1024",
        database="book_management"
    )
    cursor = connection.cursor()

    # Step 3: Create the 'books' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            quantity INT NOT NULL
        )
    """)
    connection.commit()
    return connection


# CRUD Operations
class BookModel:
    # Fetch all records
    @staticmethod
    def get_all_books():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        records = cursor.fetchall()
        conn.close()
        return records

    # Fetch book name by ID
    @staticmethod
    def get_book_name_by_id(book_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM books WHERE id = %s", (book_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # Search books by partial name
    @staticmethod
    def search_books_by_name(partial_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT id, name, quantity FROM books WHERE name LIKE %s"
        cursor.execute(query, (f"%{partial_name}%",))
        results = cursor.fetchall()
        conn.close()
        return results

    # Add or Update a book
    @staticmethod
    def add_or_update_book(name, quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, quantity FROM books WHERE name = %s", (name,))
        result = cursor.fetchone()

        if result:
            new_quantity = result[1] + quantity
            cursor.execute("UPDATE books SET quantity = %s WHERE id = %s", (new_quantity, result[0]))
        else:
            cursor.execute("INSERT INTO books (name, quantity) VALUES (%s, %s)", (name, quantity))
        conn.commit()
        conn.close()

    # Delete or Decrease book count
    @staticmethod
    def delete_or_decrease_book_by_id(book_id, quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, quantity FROM books WHERE id = %s", (book_id,))
        result = cursor.fetchone()

        if result:
            new_quantity = result[1] - quantity
            if new_quantity > 0:
                cursor.execute("UPDATE books SET quantity = %s WHERE id = %s", (new_quantity, book_id))
            else:
                cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()
        conn.close()

    # Update book name
    @staticmethod
    def update_book_name_by_id(book_id, new_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET name = %s WHERE id = %s", (new_name, book_id))
        conn.commit()
        conn.close()


# Streamlit Interface
def main():
    st.title("Book Management System")

    # Add or Update Book
    st.subheader("Add or Update a Book")
    with st.form("add_update_form", clear_on_submit=True):
        name = st.text_input("Enter Book Name:")
        quantity = st.number_input("Enter Quantity to Add:", min_value=1, step=1)
        submitted = st.form_submit_button("Add/Update Book")
        if submitted and name:
            BookModel.add_or_update_book(name, quantity)
            st.success(f"'{name}' has been added/updated successfully!")

    # Instant Update and Delete Operations
    st.subheader("Instant Update/Delete Operations")

    # Delete or Decrease Book Quantity
    del_id = st.text_input(
        "Enter Book ID to Delete/Decrease:", key="delete_id", 
        on_change=lambda: st.session_state.update({"del_name": BookModel.get_book_name_by_id(int(st.session_state.delete_id))})
    )
    del_quantity = st.number_input("Enter Quantity to Remove:", min_value=1, step=1, key="del_quantity")
    if del_id.isdigit() and "del_name" in st.session_state:
        st.write(f"Book Name: **{st.session_state.del_name}**")
    if st.button("Delete/Decrease Book"):
        if del_id and del_id.isdigit():
            BookModel.delete_or_decrease_book_by_id(int(del_id), del_quantity)
            st.success(f"Book with ID {del_id} has been updated/deleted!")
        else:
            st.warning("Invalid Book ID. Please try again.")

    # Update Book Name
    update_id = st.text_input(
        "Enter Book ID to Update:", key="update_id",
        on_change=lambda: st.session_state.update({"update_name": BookModel.get_book_name_by_id(int(st.session_state.update_id))})
    )
    if update_id.isdigit() and "update_name" in st.session_state:
        st.write(f"Current Book Name: **{st.session_state.update_name}**")
    new_name = st.text_input("Enter New Book Name:")
    if st.button("Update Book Name"):
        if update_id and update_id.isdigit():
            BookModel.update_book_name_by_id(int(update_id), new_name)
            st.success(f"Book with ID {update_id} has been updated to '{new_name}'!")
        else:
            st.warning("Invalid Book ID. Please try again.")

    # Instant Search Operation
    st.subheader("Search Books")
    search_term = st.text_input(
        "Enter part of the book name to search:", key="search_term", 
        on_change=lambda: st.session_state.update({"search_results": BookModel.search_books_by_name(st.session_state.search_term)})
    )
    if "search_results" in st.session_state:
        if st.session_state.search_results:
            st.write("Search Results:")
            for book in st.session_state.search_results:
                st.write(f"ID: {book[0]}, Name: {book[1]}, Quantity: {book[2]}")
        else:
            st.info("No books found matching your search criteria.")

    # Display Book Records
    st.subheader("Book List")
    books = BookModel.get_all_books()
    if books:
        data = [{"ID": book[0], "Name of the Book": book[1], "Quantity": book[2]} for book in books]
        st.dataframe(data)
    else:
        st.info("No records found in the table.")

    st.write("---")


# Run the app
if __name__ == "__main__":
    main()