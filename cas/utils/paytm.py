import pandas as pd
import re
import tabula


def currencyToFloat(text):
    text = re.sub(r"[(].*[)]", "", text)
    text = re.sub(r"[\s,₹]", "", text)
    return float(text)


def paytm(fileURL, PASSWORD):

    pdf = tabula.read_pdf(fileURL, password=PASSWORD, pages="all")
    part_one = None
    part_two = None
    for tabel in pdf:
        try:
            if tabel.shape[1] < 5:
                continue
            # print(tabel.shape)
            tabel = pd.DataFrame(tabel)

            portfolio_index = (
                tabel["Unnamed: 0"]
                .str.contains("^Portfolio Details")
                .apply(lambda x: True if x == True else False)
                .idxmax()
            )
            if portfolio_index > 0:
                part_one = tabel[portfolio_index + 2 : -1]

            total_index = (
                tabel["Unnamed: 0"]
                .str.contains("^Total")
                .apply(lambda x: True if x == True else False)
                .idxmax()
            )
            if total_index > 0:
                part_two = tabel[1:total_index]
                break

        except:
            pass

    result = (
        part_one[
            [
                "Unnamed: 0",
                "Unnamed: 1",
                "Unnamed: 2",
                "Unnamed: 3",
                "Unnamed: 4",
                "Unnamed: 5",
            ]
        ]
        ._append(
            part_two[
                [
                    "Unnamed: 0",
                    "Unnamed: 1",
                    "Unnamed: 2",
                    "Unnamed: 3",
                    "Unnamed: 4",
                    "Unnamed: 5",
                ]
            ],
            ignore_index=True,
        )
        .rename(
            columns={
                "Unnamed: 0": "fund",
                "Unnamed: 1": "units",
                "Unnamed: 2": "NAV",
                "Unnamed: 3": "invested",
                "Unnamed: 4": "current_value",
                "Unnamed: 5": "absolute",
            }
        )
    )

    result["invested"] = result["invested"].apply(currencyToFloat)
    result["NAV"] = result["NAV"].apply(currencyToFloat)
    result["current_value"] = result["current_value"].apply(currencyToFloat)
    result["absolute"] = result["absolute"].apply(currencyToFloat)
    result["fund"] = result["fund"].apply(lambda x: re.sub(r"[\r\n]", " ", x))

    result["absolute percent"] = round(
        (result["absolute"] / result["invested"]) * 100, 2
    )

    result = result.astype({"units": "float"})
    return result
