from deriv_sdk.market import TickHistory, TicksHistoryResponse


def test_tick_history_response() -> None:
    response = {
        "history": {
            "prices": [
                100.1,
                100.2,
                100.3,
            ],
            "times": [
                1,
                2,
                3,
            ],
        }
    }

    history = TicksHistoryResponse.parse_history(response)

    assert isinstance(history, TickHistory)

    assert history.count == 3
    assert len(history.prices) == 3
    assert len(history.times) == 3

    assert history.prices == [
        100.1,
        100.2,
        100.3,
    ]

    assert history.times == [
        1,
        2,
        3,
    ]
