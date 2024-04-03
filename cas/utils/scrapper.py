import pandas as pd
from ..models import cas_document, cas_summary

from django.db import IntegrityError, transaction

##local files
from .cams import cams
from .paytm import paytm


def main(file, password: str, fileType: str = "paytm"):

    match (fileType):
        case "paytm":
            old_df = paytm(file, password)
        case _:
            old_df = cams(file, password)

    try:
        old_df = old_df.groupby("fund", as_index=False).agg(
            {
                "folio": "first",
                "closing_balance": "sum",
                "invested": "sum",
                "current_value": "sum",
                "nav_date": "first",
                "advisor": "first",
            }
        )
    except:
        print("multiple funds not found")
        pass

    try:
        old_df["allocation"] = round(
            (old_df["current_value"] / old_df["current_value"].sum()) * 100, 2
        )
    except:
        print("couldn't able to create allocation")
        pass
    # try:
    #     with transaction.atomic():
    #         doc = cas_document(name="".join(file.name.split(".")[:-1]))
    #         doc.save()
    #         records = old_df.to_dict(orient="records")
    #         model_instances = [
    #             cas_summary(**record, document=doc) for record in records
    #         ]
    #         cas_summary.objects.bulk_create(model_instances)
    # except IntegrityError:
    #     pass
    return old_df.to_csv()
