from account import (
	create_account,
	search_account,
	balance_check,
	update_account,
	delete_account
)

from transaction import (
	deposit,
	withdraw,
	transaction_history
)


def main():

	while True:
		try:

			print("\n================================")
			print("     BANK MANAGEMENT SYSTEM")
			print("================================")

			print("1. Create Account")
			print("2. Search Account")
			print("3. Deposit")
			print("4. Withdraw")	
			print("5. Balance Check")
			print("6. Transaction History")
			print("7. Update Account")
			print("8. Delete Account")
			print("9. Exit")

			choice=input("Enter your choice : ")

			if choice=="1":
				create_account()

			elif choice=="2":
				search_account()

			elif choice=="3":
				deposit()

			elif choice=="4":
				withdraw()

			elif choice=="5":
				balance_check()

			elif choice=="6":
				transaction_history()

			elif choice=="7":
				update_account()

			elif choice=="8":
				delete_account()

			elif choice=="9":
				print("Thank you for using Bank Management System.")
				break

			else:
				print("Invalid choice. Please choose between 1 and 9.")

		except KeyboardInterrupt:
			print("\nProgram stopped by user.")
			break

		except Exception as e:
			print("Unexpected error occurred.")
			print("Error :",e)

main()
