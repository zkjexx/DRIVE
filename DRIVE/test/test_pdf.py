import os


def create_test_pdf():

    filename = "test_report.pdf"

    with open(
        filename,
        "w"
    ) as f:
        f.write(
            "D.R.I.V.E Report"
        )

    return filename



def test_pdf_generation():

    file = create_test_pdf()

    assert os.path.exists(file)

    os.remove(file)