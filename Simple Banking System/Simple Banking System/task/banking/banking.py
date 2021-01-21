import random
import sqlite3
from sqlite3 import Error

DBNAME = './card.s3db'


class SBS(object):
    CC_START = '400000'
    CC_LENGTH = 16


    def __init__(self):
        random.seed()
        # self.accounts = []
        self.db_init()
        self.main_menu()
        self.curr_acct_id: int = None
        self.curr_acct_num: str = None
        self.curr_acct_bal: int = None


    @staticmethod
    def create_connection(db_file: str = DBNAME) -> object:
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return conn


    def db_init(self) -> None:
        conn = self.create_connection()
        cur = conn.cursor()
        # cur.execute('DROP TABLE IF EXISTS card')  # <--- dropping table is for TESTING only
        sql = 'CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)'
        with conn:
            cur.execute(sql)
            # conn.commit()     # <--- not necessary with context manager
        conn.close()


    def main_menu(self) -> None:
        while True:
            inp = input('\n1. Create an account\n2. Log into account\n0. Exit\n')
            if inp == '1':
                self.create_account()
            elif inp == '2':
                self.log_to_account()
            elif inp == '0':
                print('\nBye!')
                exit()


    def create_account(self) -> int:
        cc_num = self.gen_cardno(self.CC_LENGTH, self.CC_START)
        cc_pin = self.gen_numbers(4)
        # self.accounts.append((cc_num, cc_pin))
        sql = ''' INSERT INTO card(number, pin) VALUES(?,?) '''
        conn = self.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(sql, (cc_num, cc_pin))
        conn.close()
        print('\nYour card has been created')
        print(f'Your card number:\n{cc_num}')
        print(f'Your card PIN:\n{cc_pin}')
        return cur.lastrowid


    def gen_cardno(self, length: int = 16, start_seq: str = '') -> str:
        """Generates card number of length=length with starting part=start_seq"""
        acct_n = self.gen_numbers(length - len(start_seq) - 1)
        cc = start_seq + acct_n
        cc += self.add_luhn(cc)
        return cc


    @staticmethod
    def gen_numbers(length: int = 4) -> str:
        """Generates a string of random integers from range 0-9"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])


    @staticmethod
    def add_luhn(seq: str) -> str:
        """Gets input sequence and returns additional checksum number using Luhn algorithm """
        total = 0
        for i, n in enumerate(seq):
            # drop last digit
            n = int(n[:1])
            # multiply odd digits by 2
            n = n * 2 if not (i % 2) else n
            # subtract 9 from numbers over 9
            n = (n - 9) if n > 9 else n
            total += n
        # if the total modulus 10 equals zero, then the number is valid
        # return last digit in case the sum's modulus 10 is _already_ zero (e.g. total=40)
        return str(10 - total % 10)[-1:]


    def log_to_account(self) -> None:
        cc_num = input('\nEnter your card number:\n')
        cc_pin = input('Enter your PIN:\n')
        sql = ''' SELECT id, number, balance, pin FROM card WHERE number=? AND pin=? '''
        conn = self.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(sql, (cc_num, cc_pin))
            acct = cur.fetchone()
        conn.close()
        if acct:
            # save account details in class variables in order to avoid unnecessary SQL calls
            self.curr_acct_id = acct[0]
            self.curr_acct_num = acct[1]
            self.curr_acct_bal = acct[2]
            print('\nYou have successfully logged in!\n')
            self.loggedin_menu()
        else:
            print('\nWrong card number or PIN!\n')
            self.main_menu()


    def loggedin_menu(self) -> None:
        """ Menu when cx is logged in to the account """
        while True:
            inp = input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n')
            if inp == '1':
                self.print_balance()
            elif inp == '2':
                self.add_income()
            elif inp == '3':
                self.do_transfer()
            elif inp == '4':
                self.close_account()
                print('\nThe account has been closed!\n')
                break
            elif inp == '5':
                self.curr_acct_id = None
                print('You have successfully logged out!\n')
                break
            elif inp == '0':
                print('\nBye!')
                exit()


    def print_balance(self) -> None:
        print(f'\nBalance: {self.curr_acct_bal}')


    def add_income(self):
        credit = int(input('\nEnter income:\n'))
        sql_update = ''' UPDATE card SET balance = ? WHERE id = ? '''
        bal_new = self.curr_acct_bal + credit
        conn = self.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(sql_update, (bal_new, self.curr_acct_id))
            self.curr_acct_bal = bal_new
        conn.close()
        print('Income was added!')


    def do_transfer(self):
        cc_num = input('\nTransfer\nEnter card number:\n')

        # If the receiver's card number does not pass the Luhn algorithm
        if cc_num[-1] != self.add_luhn(cc_num[:-1]):
            print('Probably you made a mistake in the card number. Please try again!\n')
            return -1

        sql_by_number = ''' SELECT id, number, balance FROM card WHERE number=? '''
        sql_update = ''' UPDATE card SET balance = ? WHERE id = ? '''

        # retrieve info on target account
        conn = self.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(sql_by_number, (cc_num,))
            target = cur.fetchone()  # target acct. info
        conn.close()

        # If the receiver's card number does not exist
        if not target:
            print('Such a card does not exist.\n')
            return -1
        else:
            target_id, target_bal = target[0], target[2]

        source_cc_num = self.curr_acct_num
        source_bal = self.curr_acct_bal

        # If the user tries to transfer money to the same account
        if cc_num == source_cc_num:
            print("You can't transfer money to the same account!\n")
            return -1

        # check balance
        amount_to_transfer = int(input('Enter how much money you want to transfer:\n'))
        if amount_to_transfer > source_bal:
            print('Not enough money!\n')
            return -1

        # do transfer
        target_bal, source_bal = target_bal + amount_to_transfer, source_bal - amount_to_transfer
        conn = self.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(sql_update, (source_bal, self.curr_acct_id))
            cur.execute(sql_update, (target_bal, target_id))
            self.curr_acct_bal = source_bal
        conn.close()
        print('Success!\n')
        return 0


    def close_account(self):
        sql1 = ''' DELETE FROM card WHERE id=? '''
        conn = self.create_connection()
        cur = conn.cursor()
        with conn:
            cur.execute(sql1, (self.curr_acct_id,))
        conn.close()
        self.curr_acct_id = None


bank1 = SBS()
