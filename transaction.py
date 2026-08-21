from database import db
from mysql.connector import Error


def deposit():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no=input("Enter account number :") 
        if account_no=="":
            print("Account number cannot be empty.")
            return
        if not account_no.isdigit():
            print("Account number only have digits.")
            return

        query="select *from accounts where account_no =%s"
        values=(account_no,)
        cursor=db.cursor()
        cursor.execute(query,values)
        result=cursor.fetchone()
        if not result:
            print("Account not found.")
            return

        amount=input("Enter deposit amount :")
        if amount=="":
            print("Amount cannot be empty.")
            return

        if  not amount.isdigit():
            print("Amount must contain only digits.")
            return

        amount=int(amount)

        if amount <=0:
            print("Amount must be greater than 0.")
            return

        new_balance=result[5]+amount

        query="update accounts set balance=%s where account_no=%s"
        values=(new_balance,account_no)
        cursor.execute(query,values)

        query="insert into transactions(account_no,transaction_type,amount) values(%s,%s,%s)"
        values=(account_no,"deposit",amount)
        cursor.execute(query,values)

        db.commit()

        print("Amount deposited successfully.")
        print("New balance :",new_balance)

    except Error as e:
        db.rollback()
        print("Database error while depositing amount.")
        print("Error :",e)

    except Exception as e:
        db.rollback()
        print("Unexpected error occurred.")
        print("Error :",e)

    finally:
        if cursor is not None:
            cursor.close()


def withdraw():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no=input("Enter account number :") 
        if account_no=="":
            print("Account number cannot be empty.")
            return
        if not account_no.isdigit():
            print("Account number only have digits.")
            return

        query="select *from accounts where account_no =%s"
        values=(account_no,)
        cursor=db.cursor()
        cursor.execute(query,values)
        result=cursor.fetchone()
        if not result:
            print("Account not found.")
            return

        amount=input("Enter withdrawal amount :")
        if amount=="":
            print("Amount cannot be empty.")
            return

        if  not amount.isdigit():
            print("Amount must contain only digits.")
            return

        amount=int(amount)

        if amount <=0:
            print("Amount must be greater than 0.")
            return

        if amount > result[5]:
            print("Insufficient balance.")
            return

        new_balance=result[5]-amount

        query="update accounts set balance=%s where account_no=%s"
        values=(new_balance,account_no)
        cursor.execute(query,values)

        query="insert into transactions(account_no,transaction_type,amount) values(%s,%s,%s)"
        values=(account_no,"withdraw",amount)
        cursor.execute(query,values)

        db.commit()

        print("Amount Withdrawal successfully.")
        print("New balance :",new_balance)

    except Error as e:
        db.rollback()
        print("Database error while withdrawing amount.")
        print("Error :",e)

    except Exception as e:
        db.rollback()
        print("Unexpected error occurred.")
        print("Error :",e)

    finally:
        if cursor is not None:
            cursor.close()


def transaction_history():

    if db is None or not db.is_connected():
        print("Database is not connected.")
        return

    cursor = None

    try:

        account_no=input("Enter account number :")
        if account_no=="":
            print("Account number cannot be empty.")
            return
        if not account_no.isdigit():
            print("Account number only have digits.")
            return

        cursor=db.cursor()

        query="select *from accounts where account_no =%s"
        values=(account_no,)
        cursor.execute(query,values)

        result=cursor.fetchone()
        if not result:
            print("Account not found.")
            return

        query="select *from transactions where account_no=%s order by transaction_date desc"
        values=(account_no,)
        cursor.execute(query,values)

        result=cursor.fetchall()

        if not result:
            print("No transactions found.")
            return

        print("\n----- Transaction History -----")

        for transaction in result:
            print("Transaction ID :",transaction[0])
            print("Account No     :",transaction[1])
            print("Type           :",transaction[2])
            print("Amount         :",transaction[3])
            print("Date           :",transaction[4])
            print("-------------------------------")

    except Error as e:
        print("Database error while fetching transaction history.")
        print("Error :",e)

    except Exception as e:
        print("Unexpected error occurred.")
        print("Error :",e)

    finally:
        if cursor is not None:
            cursor.close()