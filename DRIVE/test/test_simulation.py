def simulate_cases(
    cases,
    increase
):

    return cases * (1 + increase)



def test_simulation():

    result = simulate_cases(
        cases=100,
        increase=0.20
    )

    assert result == 120



def test_zero_change():

    result = simulate_cases(
        cases=100,
        increase=0
    )

    assert result == 100