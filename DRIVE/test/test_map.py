import folium
import pandas as pd


def test_map_rendering():

    df = pd.DataFrame({
        "Barangay": [
            "Commonwealth",
            "Batasan Hills"
        ],
        "Predicted_Cases": [
            50,
            60
        ]
    })

    m = folium.Map(
        location=[14.65, 121.05],
        zoom_start=12
    )

    assert isinstance(
        m,
        folium.Map
    )

    assert len(df) > 0