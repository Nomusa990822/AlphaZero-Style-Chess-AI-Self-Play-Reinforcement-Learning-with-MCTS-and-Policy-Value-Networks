import pytest
from benchmark_search_configs import estimate_simulations, parse_floats, parse_ints


def test_budget_counts_all_modes_and_configurations():
    assert estimate_simulations(13, [25, 50], [1.0, 1.5]) == 3900


@pytest.mark.parametrize("args", [(0, [25], [1.0]), (2, [], [1.0]), (2, [1], [])])
def test_budget_rejects_empty_dimensions(args):
    with pytest.raises(ValueError):
        estimate_simulations(*args)


@pytest.mark.parametrize("value", ["", "0", "-2", "1,1", "x"])
def test_integer_parser_rejects_invalid_values(value):
    with pytest.raises(Exception):
        parse_ints(value, "--simulations")


@pytest.mark.parametrize("value", ["", "0", "-1", "1.0,1.0", "x"])
def test_float_parser_rejects_invalid_values(value):
    with pytest.raises(Exception):
        parse_floats(value, "--c-puct")


def test_parsers_accept_valid_values():
    assert parse_ints("25, 50", "--simulations") == [25, 50]
    assert parse_floats("1.0, 1.5", "--c-puct") == [1.0, 1.5]
