def classify_risk(cases, mean, std):

    if cases < mean:
        return "Safe"

    elif cases < mean + std:
        return "Moderate"

    elif cases < mean + (2 * std):
        return "High"

    else:
        return "Extreme"



def test_risk_classification():

    risk = classify_risk(
        cases=60,
        mean=20,
        std=10
    )

    assert risk == "Extreme"


def test_low_risk():

    risk = classify_risk(
        cases=5,
        mean=20,
        std=10
    )

    assert risk == "Safe"