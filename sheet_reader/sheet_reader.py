# Reads data in google sheet.
import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

class GoogleSheetReader:
    def __init__(self, creds_json_path: str, sheet_name: str):
        self.creds_json_path = creds_json_path
        self.sheet_name = sheet_name
        self.client = self._authorize()
        self.sheet = self.client.open(sheet_name)

    def _authorize(self):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
        creds = Credentials.from_service_account_file(self.creds_json_path, scopes=scopes)
        return gspread.authorize(creds)

    def read_worksheet(self, worksheet_name: str = "Sheet1"):
        worksheet = self.sheet.worksheet(worksheet_name)
        return worksheet.get_all_values()

    def read_columns(self, worksheet_name: str, columns: list):
        """
        columns: list of column letters or indices (e.g., ['A', 'C'] or [1, 3])
        """
        worksheet = self.sheet.worksheet(worksheet_name)
        data = []
        for col in columns:
            if isinstance(col, int):
                col_letter = gspread.utils.rowcol_to_a1(1, col)[0]
            else:
                col_letter = col
            col_values = worksheet.col_values(gspread.utils.a1_to_rowcol(f"{col_letter}1")[1])
            data.append(col_values)
        return data

    def read_rows(self, worksheet_name: str, rows: list):
        """
        rows: list of row indices (1-based)
        """
        worksheet = self.sheet.worksheet(worksheet_name)
        data = []
        for row in rows:
            data.append(worksheet.row_values(row))
        return data

    def read_cells(self, worksheet_name: str, cells: list):
        """
        cells: list of cell addresses (e.g., ['A1', 'B2'])
        """
        worksheet = self.sheet.worksheet(worksheet_name)
        data = []
        for cell in cells:
            data.append(worksheet.acell(cell).value)
        return data
    
    def read_my_portfolio(self, worksheet_name: str = "Trade Records"):
        """Read my holdings to decide when to close positions.
        """
        # worksheet_data in array format.
        worksheet_data = self.read_worksheet(worksheet_name)

        if not worksheet_data or len(worksheet_data) < 2:
            return pd.DataFrame()  # Return empty DataFrame if no data.
        df = pd.DataFrame(worksheet_data[1:], columns=worksheet_data[0])
        return df
    
    def read_my_current_holdings(self):
        """From my portfolio, filter current holdings.
        """
        my_portfolio = self.read_my_portfolio()
        # Filter condition: US stock, no out date.
        return my_portfolio[
            (my_portfolio["Broker"] == "IBKR") & (my_portfolio["Out date"] == "")
        ]
    
    def read_my_watchlist(self, worksheet_name: str = "Stock Eval"):
        """Read my watchlist to decide when to open positions.
        """
        return self.read_worksheet(worksheet_name)


if __name__ == "__main__":
    # Sheets info.
    sheet_be_richer = 'be_richer'
    tab_trade_records = 'Trade Records'
    tab_stock_eval = 'Stock Eval'

    creds_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        "../wordpress-hosting-302807-2a5d57c336dd.json"))
    reader = GoogleSheetReader(creds_path, sheet_be_richer)

    # Read my current holdings.
    my_current_holdings = reader.read_my_current_holdings()
    print("Portfolio:", my_current_holdings)
