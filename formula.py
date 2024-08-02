from datetime import datetime
from monthdelta import monthdelta
from typing import Iterator, Any

date_format = '%d.%m.%Y'


def str_to_date(value: str) -> datetime:
    return datetime.strptime(value, date_format)


def date_to_str(date: datetime) -> str:
    return date.strftime(date_format)


def rounded_float_or_int(amount: float) -> float | int:
    """ в задании в примере ответа первое значение без дробной части, хотя по сути своей это float
    json-сериализатор выводит float всегда с точкой, даже если он целый.
    Если это требование, а не ошибка в задании, то эта функция в таком случае возвращает int, а не float
    """
    int_amount = int(round(amount, 0))
    rounded_amount = round(amount, 2)
    return int_amount if int_amount == rounded_amount else rounded_amount


class ValidationError(Exception):
    pass


def validate_and_return_params(params: dict) -> tuple[datetime, int, float, float]:
    """ разбор параметров запроса, полученных от RequestParser из flask_restful
    параметры имеют тип Namespace, восходящий к dict. Namespace как таковой не нужен, достаточно словаря.
    В случае невалидности входных данных выбрасывается исключение ValidationError,
    иначе возвращается кортеж параметров для deposit
    """
    try:
        date = str_to_date(params.get('date'))
    except Exception:
        raise ValidationError("Параметр 'date' должен быть строкой в формате 'dd.mm.YYYY'")

    def validate_range_param(name: str, type_, low, high) -> Any:
        try:
            value = type_(params.get(name))
            assert low <= value <= high
            return value
        except Exception:
            raise ValidationError(f"Параметр '{name}' должен быть {type_.__name__} от {low} до {high}")

    periods = validate_range_param('periods', int, 1, 60)
    # так, поскольку в задании написано (по ошибке?), что amount имеет тип Integer, хотя по сути своей Float
    amount = float(validate_range_param('amount', int, 10000, 3000000))
    rate = validate_range_param('rate', float, 1, 8)

    return date, periods, amount, rate


def deposit(date: datetime, periods: int, amount: float, rate: float) -> Iterator[tuple[datetime, float]]:
    """ Aлгоритм расчёта депозита из example.xlsx
    возвращяются данные как есть, без форматирования и округления.
    в качетсве аналога функции EDATE/ДАТАМЕС из Excel использовал пакет MonthDelta
    """
    for i in range(periods):
        amount *= 1 + rate / 12 / 100
        yield date + monthdelta(i), amount
