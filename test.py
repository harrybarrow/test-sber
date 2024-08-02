from app import app
from formula import validate_and_return_params, ValidationError, deposit

import unittest
import pandas as pd
import json


class FormulaTestCase(unittest.TestCase):

    def test_validation(self):
        data_ok = {
            "date": "31.01.2021",
            "periods": 3,
            "amount": 10000,
            "rate": 6
        }
        # валидные данные - возвращается tuple[datetime, int, float, float]
        result = validate_and_return_params(data_ok)
        self.assertEqual(len(result), 4)

        data = dict(data_ok)
        data["rate"] = 10  # испортили rate, вне диапазона
        with self.assertRaises(ValidationError) as context:
            validate_and_return_params(data)
        self.assertTrue("'rate'" in str(context.exception))

        data = dict(data_ok)
        data["amount"] = "10000.0"  # испортили amount, не Integer
        with self.assertRaises(ValidationError) as context:
            validate_and_return_params(data)
        self.assertTrue("'amount'" in str(context.exception))

        data = dict(data_ok)
        del data["periods"]  # испортили periods, удалили совсем
        with self.assertRaises(ValidationError) as context:
            validate_and_return_params(data)
        self.assertTrue("'periods'" in str(context.exception))

        data = dict(data_ok)
        data["date"] = "31/01/2021"  # испортили date, неверный формат
        with self.assertRaises(ValidationError) as context:
            validate_and_return_params(data)
        message = "Параметр 'date' должен быть строкой в формате 'dd.mm.YYYY'"
        self.assertTrue(message in str(context.exception))

    def test_deposit(self):
        # сравнение сгенерированных данных с алгоритмом расчета депозита из Excel
        df = pd.read_excel("spec/example.xlsx", header=None)
        # параметры в ячейках C2..C5
        amount = df.iloc[1, 2]
        periods = df.iloc[2, 2]
        rate = df.iloc[3, 2]
        date = df.iloc[4, 2]

        excel_row = 7  # расчитанные данные начиная с ячейки C8
        for deposit_date, deposit_amount in deposit(date, periods, amount, rate):
            excel_date = df.iloc[excel_row, 2]
            excel_amount = df.iloc[excel_row, 3]
            self.assertEqual(deposit_date, excel_date)
            self.assertEqual(deposit_amount, excel_amount)
            excel_row += 1


class AppTestCase(unittest.TestCase):
    data = {
        "date": "31.01.2021",
        "periods": 3,
        "amount": 10000,
        "rate": 6
    }

    def test_api_ok(self):
        tester = app.test_client(self)
        response = tester.get(app.api_url, content_type='application/json', data=json.dumps(self.data))
        self.assertEqual(response.status_code, 200)
        result = response.json
        self.assertEqual(len(result), self.data.get('periods'))
        self.assertEqual(result.get("28.02.2021"), 10100.25)

    def test_missed_params(self):
        tester = app.test_client(self)
        response = tester.get(app.api_url, content_type='application/json', data=json.dumps({}))
        self.assertEqual(response.status_code, 400)
        expected_result = {'error': "Параметр 'date' должен быть строкой в формате 'dd.mm.YYYY'"}
        self.assertEqual(response.json, expected_result)

    def test_bad_method(self):
        tester = app.test_client(self)
        response = tester.post(app.api_url, content_type='application/json', data=json.dumps(self.data))
        self.assertEqual(response.status_code, 405)
        expected_result = {'message': 'The method is not allowed for the requested URL.'}
        self.assertEqual(response.json, expected_result)

    def test_bad_content_type(self):
        tester = app.test_client(self)
        response = tester.get(app.api_url, data=json.dumps(self.data))
        self.assertEqual(response.status_code, 415)
        expected_result = {'message': "Did not attempt to load JSON data because the request Content-Type was not 'application/json'."}
        self.assertEqual(response.json, expected_result)


if __name__ == '__main__':
    unittest.main()
