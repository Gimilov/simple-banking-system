import random
import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);""")


class SimpleBankingSystem:

    def __init__(self):
        self.pin = None
        self.card_number = None
        self.balance = 0
        self.option = None

    def create_account(self):
        self.card_number = '400000' + "".join([str(random.randrange(10)) for i in range(9)])  # w/o checksum
        self.card_number = self.luhn_algorithm(self.card_number, 1)  # defined later
        self.pin = str(random.randrange(10000)).zfill(4)  # 4 random digits
        cur.execute("INSERT INTO card (number, pin, balance) VALUES (?, ?, ?)",
                    (self.card_number, self.pin, self.balance))
        conn.commit()
        print(f'''\nYour card has been created \nYour card number: \n{self.card_number}
Your card PIN: \n{self.pin}\n''')

    @staticmethod
    def luhn_algorithm(number, check_or_create):  # checks (0) or create (1) a card number
        if len(number) != 15 and len(number) != 16:  # 15 to create a checksum, 16 to check number
            return False
        copy_of_number = number[:]  # to save the initial version
        number = list(number)
        sum_o_numbers = 0
        for i in range(15):  # Luhn algorithm
            if int(i + 1) % 2 != 0:
                number[i] = int(number[i]) * 2
            if int(number[i]) > 9:
                number[i] = int(number[i]) - 9
            sum_o_numbers += int(number[i])
        if check_or_create == 0:
            return (sum_o_numbers + int(number[-1])) % 10 == 0
        elif check_or_create == 1:
            return "".join(map(str, copy_of_number)) + str((1000 - sum_o_numbers) % 10)  # with checksum

    def login(self, card, pin):
        cur.execute("SELECT number, pin FROM card WHERE (number=? AND pin=?);", (card, pin))
        if (card, pin) == cur.fetchone():
            print("\nYou have successfully logged in!\n")
            while self.option not in ['0', '4', '5']:
                self.logged(input('1. Balance \n2. Add income \n3. Do transfer '
                                  '\n4. Close account \n5. Log out \n0. Exit\n'), card)
            # 'card' to identify which account are we in
        else:
            print("Wrong card number or PIN!\n")

    def logged(self, option, card):
        card_tuple = (card,)  # later on this step will be omitted
        self.option = option
        if self.option == '1':
            cur.execute("SELECT balance FROM card WHERE number=?", card_tuple)
            print(f'Balance: {cur.fetchone()[0]}\n')  # only one element in this tuple
        elif self.option == '2':
            to_add = int(input('Enter income: \n'))
            cur.execute("UPDATE card SET balance = balance + ? WHERE number=?", (to_add, card))
            conn.commit()
            print("Income was added! \n")
        elif self.option == '3':
            trans_to = input('Transfer \nEnter card number: \n')
            cur.execute("SELECT EXISTS (SELECT number FROM card WHERE number=?);", (trans_to,))
            if self.luhn_algorithm(trans_to, 0) is False:
                print("Probably you made mistake in the card number. Please try again!")
            elif trans_to == card:
                print("You can't transfer money to the same account!")
            elif cur.fetchone()[0] == 0:  # zero means False
                print("Such a card does not exist.")
            else:
                cur.execute("SELECT balance FROM card WHERE number=?", (card,))
                balance_sender = cur.fetchone()[0]
                cur.execute("SELECT balance FROM card WHERE number=?", (trans_to,))
                balance_receiver = cur.fetchone()[0]
                amount = int(input('Enter how much money you want to transfer: \n'))
                if amount > balance_sender:
                    print("Not enough money!")
                else:
                    cur.execute("UPDATE card SET balance=? WHERE number=?;",
                                (balance_sender - amount, card))
                    conn.commit()
                    cur.execute("UPDATE card SET balance=? WHERE number=?",
                                (balance_receiver + amount, trans_to))
                    conn.commit()
                    print("Success!")
        elif self.option == '4':
            print("\nThe account has been closed!\n")
            cur.execute("DELETE FROM card WHERE number=?", (card,))
            conn.commit()
        elif self.option == '5':
            print('\nYou have successfully logged out!\n')
            pass


system = SimpleBankingSystem()
while True:
    print('1. Create an account.\n2. Log into account. \n0. Exit')
    decision = input()
    if decision == '1':
        system.create_account()
    elif decision == '2':
        card_no = input('\nEnter your card number: \n')
        pin_no = input('Enter your PIN number: \n').zfill(4)
        system.login(card_no, pin_no)
        if system.option == '0':
            break
    elif decision == '0':
        break
