from database import db
from mysql.connector import Error


def create_account():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:
        name = input("Enter name: ").strip()

        if not name:
            print("Name cannot be empty.")
            return

        phone_no = input("Enter phone number: ").strip()

        if not phone_no:
            print("Phone no cannot be empty.")
            return

        if not phone_no.isdigit():
            print("Phone number should contain only digits.")
            return

        if len(phone_no) != 10:
            print("Phone no must have exactly 10 digits.")
            return

        address = input("Enter address: ").strip()

        if not address:
            print("Address cannot be empty.")
            return

        account_type = input(
            "Enter account type (saving/current): "
        ).strip().lower()

        if account_type not in ("saving", "current"):
            print("Account type must be saving or current.")
            return

        cursor = db.cursor()

        query = """
            INSERT INTO accounts
            (name, phone_no, address, account_type, balance)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            name,
            phone_no,
            address,
            account_type,
            0
        )

        cursor.execute(query, values)
        db.commit()

        account_no = cursor.lastrowid

        print("Account created successfully.")
        print("Your account number is:", account_no)

    except Error as e:

        db.rollback()

        if e.errno == 1062:
            print("Phone number already exists.")
        else:
            print("Database error while creating account.")
            print("Error:", e)

    except Exception as e:

        db.rollback()

        print("Unexpected error occurred.")
        print("Error:", e)

    finally:

        if cursor is not None:
            cursor.close()


def search_account():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no = input("Enter account number: ").strip()

        if not account_no:
            print("Account no cannot be empty.")
            return

        if not account_no.isdigit():
            print("Account number should contain only digits.")
            return

        cursor = db.cursor()

        query = """
            SELECT *
            FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(query, (account_no,))

        result = cursor.fetchone()

        if not result:
            print("Account not found.")
            return

        print("Account No:", result[0])
        print("Name:", result[1])
        print("Phone No:", result[2])
        print("Address:", result[3])
        print("Account Type:", result[4])
        print("Balance:", result[5])

    except Error as e:

        print("Database error while searching account.")
        print("Error:", e)

    except Exception as e:

        print("Unexpected error occurred.")
        print("Error:", e)

    finally:

        if cursor is not None:
            cursor.close()


def balance_check():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no = input("Enter account no: ").strip()

        if not account_no:
            print("Account no cannot be empty.")
            return

        if not account_no.isdigit():
            print("Account number should contain only digits.")
            return

        cursor = db.cursor()

        query = """
            SELECT *
            FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(query, (account_no,))

        result = cursor.fetchone()

        if not result:
            print("Account not found.")
            return

        print("Account No:", result[0])
        print("Name:", result[1])
        print("Balance:", result[5])

    except Error as e:

        print("Database error while checking balance.")
        print("Error:", e)

    except Exception as e:

        print("Unexpected error occurred.")
        print("Error:", e)

    finally:

        if cursor is not None:
            cursor.close()


def update_account():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no = input("Enter account no: ").strip()

        if not account_no:
            print("Account no cannot be empty.")
            return

        if not account_no.isdigit():
            print("Account number should contain only digits.")
            return

        cursor = db.cursor()

        query = """
            SELECT *
            FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(query, (account_no,))

        result = cursor.fetchone()

        if not result:
            print("Account not found.")
            return

        print("""
1. Name
2. Phone
3. Address
4. Account Type
""")

        choice = input("Enter your choice: ").strip()

        if not choice.isdigit():
            print("Choice must contain only digits.")
            return

        choice = int(choice)

        if choice == 1:

            new_name = input("Enter new name: ").strip()

            if not new_name:
                print("Name cannot be empty.")
                return

            query = """
                UPDATE accounts
                SET name = %s
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (new_name, account_no)
            )

            db.commit()

            print("Name updated successfully.")

        elif choice == 2:

            new_phone_no = input(
                "Enter new phone no: "
            ).strip()

            if not new_phone_no:
                print("Phone no cannot be empty.")
                return

            if not new_phone_no.isdigit():
                print("Phone number should contain only digits.")
                return

            if len(new_phone_no) != 10:
                print("Phone no must have exactly 10 digits.")
                return

            query = """
                UPDATE accounts
                SET phone_no = %s
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (new_phone_no, account_no)
            )

            db.commit()

            print("Phone no updated successfully.")

        elif choice == 3:

            new_address = input("Enter new address: ").strip()

            if not new_address:
                print("Address cannot be empty.")
                return

            query = """
                UPDATE accounts
                SET address = %s
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (new_address, account_no)
            )

            db.commit()

            print("Address updated successfully.")

        elif choice == 4:

            new_account_type = input(
                "Enter new account type (saving/current): "
            ).strip().lower()

            if new_account_type not in ("saving", "current"):
                print("Choose only saving or current account.")
                return

            query = """
                UPDATE accounts
                SET account_type = %s
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (new_account_type, account_no)
            )

            db.commit()

            print("Account type updated successfully.")

        else:

            print("Invalid choice. Please choose between 1 and 4.")

    except Error as e:

        db.rollback()

        if e.errno == 1062:
            print("Phone number already exists.")
        else:
            print("Database error while updating account.")
            print("Error:", e)

    except Exception as e:

        db.rollback()

        print("Unexpected error occurred.")
        print("Error:", e)

    finally:

        if cursor is not None:
            cursor.close()


def delete_account():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no = input("Enter account no: ").strip()

        if not account_no:
            print("Account no cannot be empty.")
            return

        if not account_no.isdigit():
            print("Account number should contain only digits.")
            return

        cursor = db.cursor()

        query = """
            SELECT *
            FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(query, (account_no,))

        result = cursor.fetchone()

        if not result:
            print("Account not found.")
            return

        print("Account Holder:", result[1])
        print("Account No:", result[0])

        choice = input(
            "Are you sure you want to delete? (yes/no): "
        ).strip().lower()

        if choice == "yes":

            query = """
                DELETE FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(query, (account_no,))
            db.commit()

            print("Account deleted successfully.")

        elif choice == "no":

            print("Account deletion cancelled.")

        else:

            print("Please enter yes or no.")

    except Error as e:

        db.rollback()

        if e.errno == 1451:
            print(
                "Account cannot be deleted because transactions exist."
            )
        else:
            print("Database error while deleting account.")
            print("Error:", e)

    except Exception as e:

        db.rollback()

        print("Unexpected error occurred.")
        print("Error:", e)

    finally:

        if cursor is not None:
            cursor.close()