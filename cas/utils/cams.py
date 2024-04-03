import pdfplumber
import pandas as pd
import re


def stringToDigit(obj):
    listOfDigits = ["invested", "current_value", "closing_balance"]
    for key in listOfDigits:
        try:
            obj[key] = round(float(obj[key].replace(",", "")), 2)
        except:
            pass
    return obj


def cams(fileURL, password):
    with pdfplumber.open(fileURL, password=password) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    old_df = None
    new_df = None
    i = 0

    main_text = text.split("Folio No: ")[1:]
    for table in main_text:
        # print('----------')
        # print(table)

        obj = {}
        try:
            obj["folio"] = re.search(r"\d+", table).group()
        except:
            obj["folio"] = None

        # try:
        #   obj["pan"] = re.search(r'PAN: (\w+)', table).group(1)
        # except:
        #   obj["pan"] = None

        try:
            obj["closing_balance"] = re.search(
                r"Closing Unit Balance: ([\d,.]+)", table
            ).group(1)
        except:
            obj["closing_balance"] = None
        # print(re.search(r'Total Cost Value: ([\d,.]+)',table))
        try:
            obj["invested"] = float(
                re.search(r"Total Cost Value: ([\d,.]+)", table)
                .group(1)
                .replace(",", "")
            )
        except:
            obj["invested"] = None

        # Market Value on 23-Jan-2024: INR 142,337.05
        # try:
        #   obj["marketValue"] = float(re.search(r'Market Value on .*: INR ([\d,.]+)',table).group(1).replace(',',""))
        # except:
        #   obj["marketValue"] = None

        # try:
        #   obj["NAV"] =  re.search(r'NAV on \d{2}-\w{3}-\d{4}: INR ([\d,.]+)',table).group(1)
        # except:
        #   obj["NAV"] = None

        try:
            obj["current_value"] = float(
                re.search(r"Market Value on \d{2}-\w{3}-\d{4}: INR ([\d,.]+)", table)
                .group(1)
                .replace(",", "")
            )
        except:
            obj["current_value"] = None

        try:
            obj["nav_date"] = re.search(r"NAV on (\d{2}-\w{3}-\d{4}):", table).group(1)
            obj["nav_date"] = pd.to_datetime(obj["nav_date"], format="%d-%b-%Y").date()
        except:
            obj["nav_date"] = None
        # try:
        #   print(re.search(r"\n?[-\w()-+.,'/ :]+\n?[-\w()-+.,'/ ]+ [-] ISIN",table))
        # except:
        #   pass

        try:
            temp = re.search(
                r"\n{1}([-\w()-+.,'/ :&]+\n{1}[-\w()-+.,'/ ]+) [-] ISIN", table
            )
            # print("-----")
            # print(temp)
            if temp:
                # print(temp.group(1),re.search(r"[a-zA-Z]+ ?: ?[a-zA-Z]+\n",temp.group(1)))
                if re.search(r"[a-zA-Z]+ ?: ?[a-zA-Z]+\n", temp.group(1)):
                    temp = temp.group(1).replace(
                        re.search(r"[a-zA-Z]+ ?: ?[a-zA-Z]+\n", temp.group(1)).group(0),
                        " ",
                    )
                    # print('replaced',temp)
                else:
                    temp = temp.group(1).split("\n")[1]
                # print(temp, "\t HERE")
            else:
                temp = re.search(r"\n{1}([-\w()-+.,'/ &]+) [-] ISIN", table).group(1)
            # print(temp)
            obj["fund"] = temp.strip()

        except:
            obj["fund"] = None

        try:
            obj["advisor"] = re.search(r"Advisor: ([-\w\d]+)", table).group(1)
        except:
            obj["advisor"] = None

        obj = stringToDigit(obj)

        new_df = pd.DataFrame(data=obj, index=[i])
        # print(obj)
        # pandas
        if isinstance(old_df, pd.DataFrame):
            old_df = pd.concat([old_df, new_df], axis=0)
        else:
            old_df = new_df.copy()
        # increment
        i += 1
        # print(obj)
    return old_df
