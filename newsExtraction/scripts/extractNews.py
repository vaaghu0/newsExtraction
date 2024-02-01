import requests
from bs4 import BeautifulSoup
import dateutil.parser, dateutil.tz
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import re
from ..models import Company, News
class Scraper:
    PARSER = "html.parser"
    BASE_URL = "https://www.moneycontrol.com"
    links = []

    def __stripDetail(self, obj, key, value):
        try:
            obj[key] = value().get_text().strip().replace(r"(?:  |\n)", "")
        except AttributeError:
            obj[key] = ""

    def __getLinks(self, URL: str, links=[], page=1) -> list:
        print(URL + f"&pageno={page}")
        response = requests.get(URL + f"&pageno={page}")
        soup = BeautifulSoup(response.content.decode("utf-8", "ignore"), self.PARSER)
        currentPageLinks = soup.find_all(
            "a",
            href=re.compile(r"^/news/(?:results|recommendations|business)/.*[.]html$"),
        )
        links += currentPageLinks
        # return links
        if currentPageLinks:
            return self.__getLinks(
                URL=URL,
                links=links,
                page=page + 1,
            )
        return links

    def main(
        self,
        SYMBOL: str = "RI",
        DURATION: str = 1,
        DURATION_TYPE: str = "M",
        YEAR: str = timezone.now().year,
    ):
        URL = f"{self.BASE_URL}/stocks/company_info/stock_news.php?sc_id={SYMBOL}&durationType={DURATION_TYPE}"
        match (DURATION_TYPE):
            case "M":
                DURATION = input("Dur [1]: ") or 1
                URL += f"&duration={DURATION}"
            case "Y":
                YEAR = (
                    input(f"year [{timezone.now().year}]: ")
                    or timezone.now().year
                )
                URL += f"&Year={YEAR}"
        # print(URL)
        links = self.__getLinks(URL=URL, links=[])
        result = []
        for link in links:
            if not link.text:
                continue
            print(self.BASE_URL + link["href"])
            newsPage = BeautifulSoup(
                requests.get(self.BASE_URL + link["href"]).content.decode(
                    "utf-8", "ignore"
                ),
                self.PARSER,
            )
            obj = {}

            obj["source"] = self.BASE_URL + link["href"]

            self.__stripDetail(
                obj, "title", lambda: newsPage.select_one(".article_title")
            )
            self.__stripDetail(
                obj, "description", lambda: newsPage.select_one(".article_desc")
            )
            self.__stripDetail(
                obj, "author", lambda: newsPage.select_one(".article_author")
            )

            self.__stripDetail(
                obj, "scheduled", lambda: newsPage.select_one(".article_schedule")
            )
            # obj['scheduled'] = timezone.now()
            obj['scheduled'] = dateutil.parser.parse(obj["scheduled"],tzinfos={"CDT": dateutil.tz.gettz('Asia/Kolkata')}) if obj["scheduled"] else None
            content = []
            isLastParaCrossed = False
            paraList = []

            try:
                paraList += newsPage.select_one("#contentdata").find_all("p")
            except AttributeError:
                Warning(f"couldn't get the content of \n {link['href']}")
                pass
            try:
                paraList += newsPage.find(
                    "div", attrs={"itemprop": "articleBody"}
                ).find_all("p")
                print(paraList, URL)
            except AttributeError:
                Warning(f"couldn't get the articleBody of \n {link['href']}")
                pass
                # paraList = []

            for para in paraList:
                if isLastParaCrossed:
                    break
                try:
                    if para["class"] == "lastPara":
                        isLastParaCrossed = True
                except KeyError:
                    pass
                content.append(para.get_text())

            obj["content"] = "\n".join(content)
            result.append(obj)
            # break
        # print(result)
        return result


def run():
    symbol = input("Symbol: ")
    try:
        target_company = Company.objects.get(symbol=symbol)
    except Company.DoesNotExist:
        print(f"company with symbol {symbol} doesn't exist in table")
        print(f"1 -> create a entry in tabel")
        choice = input("choice: ")
        if not choice == "1":
            return
        name = input("name: ")
        target_company = Company.objects.create(name=name, symbol=symbol)
    print(target_company)
    scraper = Scraper()
    results = scraper.main(
        SYMBOL=target_company.symbol, DURATION_TYPE=input("Type [M]: ")
    )
    # News(title = "sefs",scheduled = timezone.now() ,company = target_company).save()
    for news in results:
        n = News(**news,company = target_company)
        print(n)
        n.save()