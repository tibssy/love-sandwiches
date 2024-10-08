import gspread
from google.oauth2.service_account import Credentials
import numpy as np


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')


def get_sales_data() -> list:
    """
    Get sales figures input from the user.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of 6 numbers separated
    by commas. The loop will repeatedly request data, until it is valid.
    """

    while True:
        print('Please enter sales data from the last market.\nData should be six numbers, separated by commas.\nExample: 10,20,30,40,50,60\n')

        data_str = input('Enter your data here: ')

        sales_data = data_str.split(',')
        validate_data(sales_data)
        if validate_data(sales_data):
            print('Data is valid!')
            break

    return [int(val) for val in sales_data]

def validate_data(values: list) -> bool:
    """
    Inside the try, converts all string values into integers.
    Raises ValueError if strings cannot be converted into int,
    or if there aren't exactly 6 values.
    """
    try:
        if (val_len := len(values)) != 6:
            raise ValueError(f'Exactly 6 values required, you provided {val_len}')
        [int(value) for value in values]
    except ValueError as e:
        print(f'Invalid data: {e}, please try again.\n')
        return False
    else:
        return True


def update_worksheet(worksheet: str, data: list) -> None:
    """
    Update worksheet, add new row with the list data provided.
    """

    print(f'Updating {worksheet} worksheet...\n')
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f'{worksheet.capitalize()} worksheet updated successfully.\n')


def calculate_surplus_data(sales_row: list) -> list:
    """
    Compare sales with stock and calculate the surplus for each item type.
    The surplus is defined as the sales figure subtracted from the stock:
    - Positive surplis indicates waste

    - Negative surplus indicates extra made when stock was sold out.
    """

    print('Calculating surplus data...\n')
    stock = SHEET.worksheet('stock').get_all_values()
    stock_row = stock[-1]

    return [int(stock) - sales for stock, sales in zip(stock_row, sales_row)]


def calculate_stock_data() -> list:
    """
    Collecting the last 5 entries for each sandwich and
    calculate the average stock for each item type, adding 10%
    """

    print('Calculating stock data...\n')

    sales_data = SHEET.worksheet('sales').get_all_values()[1:]
    last_5_entries = np.array(sales_data[-5:]).astype(int)
    return np.round(np.mean(last_5_entries, axis=0) * 1.1).astype(int).tolist()


def main():
    """
    Run all program functions
    """

    sales_data = get_sales_data()
    update_worksheet('sales', sales_data)
    new_surplus_data = calculate_surplus_data(sales_data)
    update_worksheet('surplus', new_surplus_data)
    stock_data = calculate_stock_data()
    update_worksheet('stock', stock_data)


if __name__ == '__main__':
    print('Welcome to Love Sandwiches Data Automation')
    main()
