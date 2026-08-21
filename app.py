from flask import Flask, render_template, request, redirect, url_for, flash
import os
from database import db, get_database
from mysql.connector import Error


app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")


def database_available():

    global db
    db = get_database()

    if db is None:
        return False

    try:

        if db.is_connected():
            return True

        return False

    except Error:

        return False


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/create-account", methods=["GET", "POST"])
def create_account():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone_no = request.form.get("phone_no", "").strip()
        address = request.form.get("address", "").strip()
        account_type = request.form.get("account_type", "").strip().lower()

        if name == "":
            flash("Name cannot be empty.", "error")
            return render_template("create_account.html")

        if phone_no == "":
            flash("Phone number cannot be empty.", "error")
            return render_template("create_account.html")

        if not phone_no.isdigit():
            flash("Phone number must contain only digits.", "error")
            return render_template("create_account.html")

        if len(phone_no) != 10:
            flash("Phone number must contain exactly 10 digits.", "error")
            return render_template("create_account.html")

        if address == "":
            flash("Address cannot be empty.", "error")
            return render_template("create_account.html")

        if account_type == "":
            flash("Please select an account type.", "error")
            return render_template("create_account.html")

        if account_type not in ("saving", "current"):
            flash("Account type must be Saving or Current.", "error")
            return render_template("create_account.html")

        if not database_available():

            flash("Database is not connected.", "error")
            return render_template("create_account.html")

        cursor = None

        try:

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

            return render_template(
                "success.html",
                title="Account Created Successfully",
                message="Your bank account has been created successfully.",
                details={
                    "Account Number": account_no,
                    "Name": name,
                    "Phone Number": phone_no,
                    "Account Type": account_type.title(),
                    "Initial Balance": "₹0"
                }
            )

        except Error as e:

            db.rollback()

            if e.errno == 1062:

                flash("Phone number already exists.", "error")

            else:

                print("Database error:", e)

                flash(
                    "Database error while creating account.",
                    "error"
                )

            return render_template("create_account.html")

        except Exception as e:

            db.rollback()

            print("Unexpected error:", e)

            flash("Unexpected error occurred.", "error")

            return render_template("create_account.html")

        finally:

            if cursor is not None:
                cursor.close()

    return render_template("create_account.html")


@app.route("/search-account", methods=["GET", "POST"])
def search_account():

    result = None

    if request.method == "POST":

        account_no = request.form.get(
            "account_no",
            ""
        ).strip()

        if account_no == "":

            flash(
                "Account number cannot be empty.",
                "error"
            )

            return render_template(
                "search_account.html",
                result=None
            )

        if not account_no.isdigit():

            flash(
                "Account number must contain only digits.",
                "error"
            )

            return render_template(
                "search_account.html",
                result=None
            )

        if not database_available():

            flash(
                "Database is not connected.",
                "error"
            )

            return render_template(
                "search_account.html",
                result=None
            )

        cursor = None

        try:

            cursor = db.cursor()

            query = """
                SELECT
                    account_no,
                    name,
                    phone_no,
                    address,
                    account_type,
                    balance
                FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (account_no,)
            )

            result = cursor.fetchone()

            if result is None:

                flash(
                    "Account not found.",
                    "error"
                )

            return render_template(
                "search_account.html",
                result=result
            )

        except Error as e:

            print("Database error:", e)

            flash(
                "Database error while searching account.",
                "error"
            )

            return render_template(
                "search_account.html",
                result=None
            )

        except Exception as e:

            print("Unexpected error:", e)

            flash(
                "Unexpected error occurred.",
                "error"
            )

            return render_template(
                "search_account.html",
                result=None
            )

        finally:

            if cursor is not None:
                cursor.close()

    return render_template(
        "search_account.html",
        result=result
    )


@app.route("/deposit", methods=["GET", "POST"])
def deposit():

    if request.method == "POST":

        account_no = request.form.get(
            "account_no",
            ""
        ).strip()

        amount_text = request.form.get(
            "amount",
            ""
        ).strip()

        if account_no == "":

            flash(
                "Account number cannot be empty.",
                "error"
            )

            return render_template("deposit.html")

        if not account_no.isdigit():

            flash(
                "Account number must contain only digits.",
                "error"
            )

            return render_template("deposit.html")

        if amount_text == "":

            flash(
                "Deposit amount cannot be empty.",
                "error"
            )

            return render_template("deposit.html")

        if not amount_text.isdigit():

            flash(
                "Amount must contain only digits.",
                "error"
            )

            return render_template("deposit.html")

        amount = int(amount_text)

        if amount <= 0:

            flash(
                "Amount must be greater than 0.",
                "error"
            )

            return render_template("deposit.html")

        if not database_available():

            flash(
                "Database is not connected.",
                "error"
            )

            return render_template("deposit.html")

        cursor = None

        try:

            cursor = db.cursor()

            query = """
                SELECT account_no, name, balance
                FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (account_no,)
            )

            result = cursor.fetchone()

            if result is None:

                flash(
                    "Account not found.",
                    "error"
                )

                return render_template("deposit.html")

            old_balance = result[2]

            new_balance = old_balance + amount

            update_query = """
                UPDATE accounts
                SET balance = %s
                WHERE account_no = %s
            """

            cursor.execute(
                update_query,
                (new_balance, account_no)
            )

            transaction_query = """
                INSERT INTO transactions
                (account_no, transaction_type, amount)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                transaction_query,
                (
                    account_no,
                    "deposit",
                    amount
                )
            )

            db.commit()

            return render_template(
                "success.html",
                title="Deposit Successful",
                message="Money has been deposited successfully.",
                details={
                    "Account Number": account_no,
                    "Account Holder": result[1],
                    "Deposited Amount": f"₹{amount}",
                    "Previous Balance": f"₹{old_balance}",
                    "New Balance": f"₹{new_balance}"
                }
            )

        except Error as e:

            db.rollback()

            print("Database error:", e)

            flash(
                "Database error while depositing money.",
                "error"
            )

            return render_template("deposit.html")

        except Exception as e:

            db.rollback()

            print("Unexpected error:", e)

            flash(
                "Unexpected error occurred.",
                "error"
            )

            return render_template("deposit.html")

        finally:

            if cursor is not None:
                cursor.close()

    return render_template("deposit.html")


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():

    if request.method == "POST":

        account_no = request.form.get(
            "account_no",
            ""
        ).strip()

        amount_text = request.form.get(
            "amount",
            ""
        ).strip()

        if account_no == "":

            flash(
                "Account number cannot be empty.",
                "error"
            )

            return render_template("withdraw.html")

        if not account_no.isdigit():

            flash(
                "Account number must contain only digits.",
                "error"
            )

            return render_template("withdraw.html")

        if amount_text == "":

            flash(
                "Withdrawal amount cannot be empty.",
                "error"
            )

            return render_template("withdraw.html")

        if not amount_text.isdigit():

            flash(
                "Amount must contain only digits.",
                "error"
            )

            return render_template("withdraw.html")

        amount = int(amount_text)

        if amount <= 0:

            flash(
                "Amount must be greater than 0.",
                "error"
            )

            return render_template("withdraw.html")

        if not database_available():

            flash(
                "Database is not connected.",
                "error"
            )

            return render_template("withdraw.html")

        cursor = None

        try:

            cursor = db.cursor()

            query = """
                SELECT account_no, name, balance
                FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (account_no,)
            )

            result = cursor.fetchone()

            if result is None:

                flash(
                    "Account not found.",
                    "error"
                )

                return render_template("withdraw.html")

            old_balance = result[2]

            if amount > old_balance:

                flash(
                    "Insufficient balance.",
                    "error"
                )

                return render_template("withdraw.html")

            new_balance = old_balance - amount

            update_query = """
                UPDATE accounts
                SET balance = %s
                WHERE account_no = %s
            """

            cursor.execute(
                update_query,
                (new_balance, account_no)
            )

            transaction_query = """
                INSERT INTO transactions
                (account_no, transaction_type, amount)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                transaction_query,
                (
                    account_no,
                    "withdraw",
                    amount
                )
            )

            db.commit()

            return render_template(
                "success.html",
                title="Withdrawal Successful",
                message="Money has been withdrawn successfully.",
                details={
                    "Account Number": account_no,
                    "Account Holder": result[1],
                    "Withdrawn Amount": f"₹{amount}",
                    "Previous Balance": f"₹{old_balance}",
                    "New Balance": f"₹{new_balance}"
                }
            )

        except Error as e:

            db.rollback()

            print("Database error:", e)

            flash(
                "Database error while withdrawing money.",
                "error"
            )

            return render_template("withdraw.html")

        except Exception as e:

            db.rollback()

            print("Unexpected error:", e)

            flash(
                "Unexpected error occurred.",
                "error"
            )

            return render_template("withdraw.html")

        finally:

            if cursor is not None:
                cursor.close()

    return render_template("withdraw.html")


@app.route("/balance", methods=["GET", "POST"])
def balance_check():

    result = None

    if request.method == "POST":

        account_no = request.form.get(
            "account_no",
            ""
        ).strip()

        if account_no == "":

            flash(
                "Account number cannot be empty.",
                "error"
            )

            return render_template(
                "balance.html",
                result=None
            )

        if not account_no.isdigit():

            flash(
                "Account number must contain only digits.",
                "error"
            )

            return render_template(
                "balance.html",
                result=None
            )

        if not database_available():

            flash(
                "Database is not connected.",
                "error"
            )

            return render_template(
                "balance.html",
                result=None
            )

        cursor = None

        try:

            cursor = db.cursor()

            query = """
                SELECT
                    account_no,
                    name,
                    phone_no,
                    address,
                    account_type,
                    balance
                FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(
                query,
                (account_no,)
            )

            result = cursor.fetchone()

            if result is None:

                flash(
                    "Account not found.",
                    "error"
                )

            return render_template(
                "balance.html",
                result=result
            )

        except Error as e:

            print("Database error:", e)

            flash(
                "Database error while checking balance.",
                "error"
            )

            return render_template(
                "balance.html",
                result=None
            )

        except Exception as e:

            print("Unexpected error:", e)

            flash(
                "Unexpected error occurred.",
                "error"
            )

            return render_template(
                "balance.html",
                result=None
            )

        finally:

            if cursor is not None:
                cursor.close()

    return render_template(
        "balance.html",
        result=result
    )


@app.route("/transaction-history", methods=["GET", "POST"])
def transaction_history():

    transactions = None
    account = None

    if request.method == "POST":

        account_no = request.form.get(
            "account_no",
            ""
        ).strip()

        if account_no == "":

            flash(
                "Account number cannot be empty.",
                "error"
            )

            return render_template(
                "transaction_history.html",
                transactions=None,
                account=None
            )

        if not account_no.isdigit():

            flash(
                "Account number must contain only digits.",
                "error"
            )

            return render_template(
                "transaction_history.html",
                transactions=None,
                account=None
            )

        if not database_available():

            flash(
                "Database is not connected.",
                "error"
            )

            return render_template(
                "transaction_history.html",
                transactions=None,
                account=None
            )

        cursor = None

        try:

            cursor = db.cursor()

            account_query = """
                SELECT
                    account_no,
                    name,
                    balance
                FROM accounts
                WHERE account_no = %s
            """

            cursor.execute(
                account_query,
                (account_no,)
            )

            account = cursor.fetchone()

            if account is None:

                flash(
                    "Account not found.",
                    "error"
                )

                return render_template(
                    "transaction_history.html",
                    transactions=None,
                    account=None
                )

            transaction_query = """
                SELECT
                    transaction_id,
                    account_no,
                    transaction_type,
                    amount,
                    transaction_date
                FROM transactions
                WHERE account_no = %s
                ORDER BY transaction_date DESC
            """

            cursor.execute(
                transaction_query,
                (account_no,)
            )

            transactions = cursor.fetchall()

            if not transactions:

                flash(
                    "No transactions found for this account.",
                    "info"
                )

            return render_template(
                "transaction_history.html",
                transactions=transactions,
                account=account
            )

        except Error as e:

            print("Database error:", e)

            flash(
                "Database error while fetching transactions.",
                "error"
            )

            return render_template(
                "transaction_history.html",
                transactions=None,
                account=None
            )

        except Exception as e:

            print("Unexpected error:", e)

            flash(
                "Unexpected error occurred.",
                "error"
            )

            return render_template(
                "transaction_history.html",
                transactions=None,
                account=None
            )

        finally:

            if cursor is not None:
                cursor.close()

    return render_template(
        "transaction_history.html",
        transactions=transactions,
        account=account
    )


@app.route("/update-account", methods=["GET", "POST"])
def update_account():

    if not database_available():

        flash(
            "Database is not connected.",
            "error"
        )

        return render_template(
            "update_account.html",
            accounts=[]
        )

    cursor = None

    try:

        cursor = db.cursor()

        query = """
            SELECT
                account_no,
                name,
                phone_no,
                address,
                account_type,
                balance
            FROM accounts
            ORDER BY account_no ASC
        """

        cursor.execute(query)

        accounts = cursor.fetchall()

    except Error as e:

        print("Database error:", e)

        flash(
            "Database error while loading accounts.",
            "error"
        )

        accounts = []

    except Exception as e:

        print("Unexpected error:", e)

        flash(
            "Unexpected error occurred.",
            "error"
        )

        accounts = []

    finally:

        if cursor is not None:
            cursor.close()

    return render_template(
        "update_account.html",
        accounts=accounts
    )


@app.route("/edit-account/<int:account_no>", methods=["GET", "POST"])
def edit_account(account_no):

    if not database_available():

        flash(
            "Database is not connected.",
            "error"
        )

        return redirect(
            url_for("update_account")
        )

    cursor = None

    try:

        cursor = db.cursor()

        query = """
            SELECT
                account_no,
                name,
                phone_no,
                address,
                account_type,
                balance
            FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(
            query,
            (account_no,)
        )

        account = cursor.fetchone()

        if account is None:

            flash(
                "Account not found.",
                "error"
            )

            return redirect(
                url_for("update_account")
            )

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            phone_no = request.form.get(
                "phone_no",
                ""
            ).strip()

            address = request.form.get(
                "address",
                ""
            ).strip()

            account_type = request.form.get(
                "account_type",
                ""
            ).strip().lower()

            if name == "":

                flash(
                    "Name cannot be empty.",
                    "error"
                )

                return render_template(
                    "edit_account.html",
                    account=account
                )

            if phone_no == "":

                flash(
                    "Phone number cannot be empty.",
                    "error"
                )

                return render_template(
                    "edit_account.html",
                    account=account
                )

            if not phone_no.isdigit():

                flash(
                    "Phone number must contain only digits.",
                    "error"
                )

                return render_template(
                    "edit_account.html",
                    account=account
                )

            if len(phone_no) != 10:

                flash(
                    "Phone number must contain exactly 10 digits.",
                    "error"
                )

                return render_template(
                    "edit_account.html",
                    account=account
                )

            if address == "":

                flash(
                    "Address cannot be empty.",
                    "error"
                )

                return render_template(
                    "edit_account.html",
                    account=account
                )

            if account_type not in (
                "saving",
                "current"
            ):

                flash(
                    "Please select a valid account type.",
                    "error"
                )

                return render_template(
                    "edit_account.html",
                    account=account
                )

            update_query = """
                UPDATE accounts
                SET
                    name = %s,
                    phone_no = %s,
                    address = %s,
                    account_type = %s
                WHERE account_no = %s
            """

            values = (
                name,
                phone_no,
                address,
                account_type,
                account_no
            )

            cursor.execute(
                update_query,
                values
            )

            db.commit()

            flash(
                "Account updated successfully.",
                "success"
            )

            return redirect(
                url_for("update_account")
            )

        return render_template(
            "edit_account.html",
            account=account
        )

    except Error as e:

        db.rollback()

        if e.errno == 1062:

            flash(
                "Phone number already exists.",
                "error"
            )

        else:

            print("Database error:", e)

            flash(
                "Database error while updating account.",
                "error"
            )

        return redirect(
            url_for("update_account")
        )

    except Exception as e:

        db.rollback()

        print("Unexpected error:", e)

        flash(
            "Unexpected error occurred.",
            "error"
        )

        return redirect(
            url_for("update_account")
        )

    finally:

        if cursor is not None:
            cursor.close()


@app.route("/delete-account", methods=["GET", "POST"])
def delete_account():

    if not database_available():

        flash(
            "Database is not connected.",
            "error"
        )

        return render_template(
            "delete_account.html",
            accounts=[]
        )

    cursor = None

    try:

        cursor = db.cursor()

        query = """
            SELECT
                account_no,
                name,
                phone_no,
                address,
                account_type,
                balance
            FROM accounts
            ORDER BY account_no ASC
        """

        cursor.execute(query)

        accounts = cursor.fetchall()

    except Error as e:

        print("Database error:", e)

        flash(
            "Database error while loading accounts.",
            "error"
        )

        accounts = []

    except Exception as e:

        print("Unexpected error:", e)

        flash(
            "Unexpected error occurred.",
            "error"
        )

        accounts = []

    finally:

        if cursor is not None:
            cursor.close()

    return render_template(
        "delete_account.html",
        accounts=accounts
    )


@app.route(
    "/delete-account/<int:account_no>",
    methods=["POST"]
)
def delete_single_account(account_no):

    if not database_available():

        flash(
            "Database is not connected.",
            "error"
        )

        return redirect(
            url_for("delete_account")
        )

    cursor = None

    try:

        cursor = db.cursor()

        query = """
            SELECT account_no, name
            FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(
            query,
            (account_no,)
        )

        account = cursor.fetchone()

        if account is None:

            flash(
                "Account not found.",
                "error"
            )

            return redirect(
                url_for("delete_account")
            )

        transaction_query = """
            DELETE FROM transactions
            WHERE account_no = %s
        """

        cursor.execute(
            transaction_query,
            (account_no,)
        )

        account_query = """
            DELETE FROM accounts
            WHERE account_no = %s
        """

        cursor.execute(
            account_query,
            (account_no,)
        )

        db.commit()

        flash(
            f"Account {account_no} deleted successfully.",
            "success"
        )

        return redirect(
            url_for("delete_account")
        )

    except Error as e:

        db.rollback()

        print("Database error:", e)

        flash(
            "Database error while deleting account.",
            "error"
        )

        return redirect(
            url_for("delete_account")
        )

    except Exception as e:

        db.rollback()

        print("Unexpected error:", e)

        flash(
            "Unexpected error occurred.",
            "error"
        )

        return redirect(
            url_for("delete_account")
        )

    finally:

        if cursor is not None:
            cursor.close()


@app.route("/admin/accounts")
def all_accounts():

    if not database_available():

        flash(
            "Database is not connected.",
            "error"
        )

        return render_template(
            "accounts.html",
            accounts=[]
        )

    cursor = None

    try:

        cursor = db.cursor()

        query = """
            SELECT
                account_no,
                name,
                phone_no,
                address,
                account_type,
                balance
            FROM accounts
            ORDER BY account_no ASC
        """

        cursor.execute(query)

        accounts = cursor.fetchall()

        return render_template(
            "accounts.html",
            accounts=accounts
        )

    except Error as e:

        print("Database error:", e)

        flash(
            "Database error while loading accounts.",
            "error"
        )

        return render_template(
            "accounts.html",
            accounts=[]
        )

    except Exception as e:

        print("Unexpected error:", e)

        flash(
            "Unexpected error occurred.",
            "error"
        )

        return render_template(
            "accounts.html",
            accounts=[]
        )

    finally:

        if cursor is not None:
            cursor.close()


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "500.html"
    ), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )