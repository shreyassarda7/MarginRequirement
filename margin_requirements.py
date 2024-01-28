import requests
import json
import time


class Position:
    def __init__(self, *argv, **kwargs):
        """
        :param argv: Dict with keys (contract, exchange, product, qty, strikePrice, tradeType, optionType)
        :param kwargs: keys (contract, exchange, product, qty, strikePrice, tradeType, optionType)
        """
        if argv:
            self.position_dict = argv[0]
        else:
            self.position_dict = kwargs
        self.contract = self.position_dict['contract']
        self.exchange = self.position_dict['exchange']
        self.product = self.position_dict['product']
        self.qty = self.position_dict['qty']
        self.strikePrice = self.position_dict['strikePrice']
        self.tradeType = self.position_dict['tradeType']
        self.optionType = self.position_dict['optionType']


class NseMargin:
    """
    Calculates margin requirement for position using Angel Broking
    """
    def __init__(self):
        self.response = None
        self.total_position = {"position": []}
        self.json_ = None
        self.position_margin = []
        self.total_position_margin = 0
        self.margin = {}

    def visualize_margin(self):
        # Convert the data to a JSON formatted string with 4 spaces of indentation
        json_str = json.dumps(self.json_, indent=4)

        # Print the pretty-printed JSON string
        print(json_str)

    def add_individual_position(self, contract, exchange, product, qty, strike, side, option_type):
        """
        :param contract: str (For ex. "NIFTY-29FEB24")
        :param exchange: (MCX, NFO, CDS, NCDEX, BFO)
        :param product: (OPTION, FUTURE)
        :param qty: int
        :param strike: int
        :param side: (BUY, SELL)
        :param option_type: (CALL, PUT)
        :return: None
        """
        position_payload = {"contract": contract, "exchange": exchange, "product": product, "qty": qty, "strikePrice": strike, "tradeType": side, "optionType": option_type}

        if "position" in self.total_position:
            self.total_position["position"].append(position_payload)
        else:
            self.total_position["position"] = [position_payload]

    def add_position(self, position):
        """
        :param position_dict: dict
        :return: None
        """
        if isinstance(position, Position):
            position_dict = position.position_dict
        else:
            position_dict = position

        if "position" in self.total_position:
            self.total_position["position"].append(position_dict)
        else:
            self.total_position["position"] = [position_dict]

    def add_positions(self, positions: list):
        """
        :param positions: List of class Positions
        :return:
        """
        for pos in positions:
            self.add_position(pos)

    def retrieve_margin(self):
        self.total_position_margin = self.json_['totalPositionMargin']
        self.position_margin = self.json_['positionMargin']
        self.margin = self.json_['margin']

    def load_margin(self, show_response=False):
        cookies = ['exchange/NFO/product', 'OPTION/contract', 'NIFTY-1FEB24/strike-price']
        cookie_str = 'https://margin-calc-arom-prod.angelbroking.com/'

        with requests.Session() as s:
            for cookie in cookies:
                cookie_str += cookie
                s.get(cookie_str)

            time.sleep(0.1)

            self.response = s.post(
                'https://margin-calc-arom-prod.angelbroking.com/margin-calculator/SPAN',
                json=self.total_position)

            self.json_ = self.response.json()
            self.retrieve_margin()

            if show_response:
                self.visualize_margin()

    def get_total_margin(self, verbose=False):
        """
        :param verbose: Flag for showing margin request response
        :return: (int) Total margin requirement
        """
        self.load_margin(show_response=verbose)
        return self.total_position_margin


if __name__ == "__main__":
    n = NseMargin()
    p1 = Position(
        {
            "contract": "NIFTY-29FEB24", "exchange": "NFO", "product": "OPTION",
            "qty": 50, "strikePrice": 21500, "tradeType": "SELL", "optionType": "CALL"
        }
    )
    p2 = Position(contract="NIFTY-01FEB24", exchange="NFO", product="OPTION",
                  qty=50, strikePrice=21500, tradeType="SELL", optionType="CALL")
    n.add_position(p1)
    n.add_position(p2)
    n.add_positions([
        {
            "contract": "NIFTY-01FEB24", "exchange": "NFO", "product": "OPTION",
            "qty": 50, "strikePrice": 24000, "tradeType": "SELL", "optionType": "CALL"
        },
        {
            "contract": "NIFTY-29FEB24", "exchange": "NFO", "product": "OPTION",
            "qty": 50, "strikePrice": 25000, "tradeType": "SELL", "optionType": "CALL"
        }
    ])
    print(n.get_total_margin())
    print()



