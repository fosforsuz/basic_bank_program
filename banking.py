import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card 
(id integer, number text, pin text, balance integer)""")


class Bank:
    """The Bank class store user information and log in control and log in operations """

    def __init__(self):
        self.card_number = None
        self.password = None
        self.balance = 0
        self.id = 1

    def create_user(self):
        """Created random 15 digit card number and 4 digit card PIN"""
        print("\nYour card has been created")
        random.seed()
        self.card_number = "400000" + str(random.randint(100000000, 999999999))
        self.luhn_algorithm()
        self.password = str(random.randint(0000, 9999))
        """If password length smaller than 4, this line completes to 4 digit"""
        self.password = self.password + "0" * (4 - len(self.password))
        cur.execute(
            f"INSERT INTO card (id, number, pin, balance) VALUES ({self.id}, {self.card_number}, {self.password}, {self.balance})")
        conn.commit()
        print(f"Your card number:\n{self.card_number}\nYour card PIN:\n{self.password}\n")

    def luhn_algorithm(self):
        """Created last digit for card number with luhn algorithm"""
        processed_digits = []
        for index, digit in enumerate(self.card_number):
            if index % 2 == 0:
                doubled_digit = int(digit) * 2
                if doubled_digit > 9:
                    doubled_digit -= 9
                processed_digits.append(doubled_digit)
            else:
                processed_digits.append(int(digit))
        self.card_number += str(10 - sum(processed_digits) % 10) if sum(processed_digits) % 10 != 0 else str(0)

    def log_in_control(self, user_card_number, user_password):
        """Check the input from users which are card number and password"""
        cur.execute(f"SELECT number, pin FROM card WHERE number = {user_card_number} AND pin = {user_password}")
        control = cur.fetchall()
        for item in control:
            if item:
                return True
        return False

    def log_in(self, number):
        print("\nYou have successfully logged in!\n")
        while True:
            log_in_choice = int(
                input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n"))
            if log_in_choice == 1:
                print(f"Balance: {self.balance}\n")
            elif log_in_choice == 2:
                self.add_income(number)
            elif log_in_choice == 3:
                self.transfer(number)
            elif log_in_choice == 4:
                self.close_account(number)
            elif log_in_choice == 5:
                exit()
            elif log_in_choice == 0:
                return exit()

    def add_income(self, card):
        """Add money to your balance"""
        income = int(input("Enter income:\n"))
        self.balance += income
        cur.execute(f"""UPDATE card SET balance = balance + {income} WHERE number = {card}""")
        conn.commit()
        print("Income was added")

    def transfer(self, number):
        """transfer card number to card number. Also control card number which you send money"""
        transfer_number = input()
        if self.control_with_luhn(transfer_number) == False:
            print("Probably you made a mistake in the card number. Please try again!")
            return None
        if transfer_number == self.card_number:
            print("You can't transfer money to the same account!")
            return None
        cur.execute(f"""SELECT number, balance FROM card WHERE number = {transfer_number}""")
        control = cur.fetchall()
        if len(control) == 0:
            print("Such a card does not exist.")
        else:
            transfer_money = int(input("Enter how much money you want to transfer:\n"))
            if transfer_money < self.balance:
                cur.execute(
                    f"""UPDATE card SET balance = balance + {transfer_money} WHERE number = {transfer_number}""")
                cur.execute(
                    f"""UPDATE card SET balance = balance - {transfer_money} WHERE number = {number}""")
                conn.commit()
                print("Success!\n")
            else:
                print("Not enough money!\n")

    def control_with_luhn(self, number):
        """Control the number which you want to send money"""
        int_number = [int(item) for item in number]
        check_digit = int_number.pop()
        processed_digit = []
        int_number.reverse()
        for index, digit in enumerate(int_number):
            if index % 2 == 0:
                doubled_digit = int(digit) * 2
                if doubled_digit > 9:
                    doubled_digit = doubled_digit - 9
                processed_digit.append(doubled_digit)
            else:
                processed_digit.append(int(digit))
        return True if (int(check_digit) + sum(processed_digit)) % 10 == 0 else False

    def close_account(self, account):
        """remove your account from card database"""
        cur.execute(f"""DELETE FROM card WHERE number = {account}""")
        conn.commit()
        print("The account has been closed!")


if __name__ == "__main__":
    while True:
        user = Bank()
        choice = int(input("1. Create an account\n2.Log into account\n0. exit\n"))
        if choice == 1:
            user.create_user()
        elif choice == 2:
            user_number = input("\nEnter your card number:\n")
            password = input("Enter your card PIN:\n")
            if user.log_in_control(user_number, password):
                user.log_in(user_number)
            else:
                print("\nWrong card number or PIN!\n")
        elif choice == 0:
            print("\nBye!")
            exit()
