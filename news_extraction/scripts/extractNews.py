import requests
from bs4 import BeautifulSoup
import dateutil.parser, dateutil.tz
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import re
from ..models import Company, News
import warnings
from concurrent.futures import ThreadPoolExecutor
import asyncio

class Scraper:
    PARSER = "html.parser"
    BASE_URL = "https://www.moneycontrol.com"
    links = []
    __pagesData = []
    __targetCompany = None

    def setTargetCompany(self,targetCompany):
        self.__targetCompany = targetCompany
    
    def __saveNews(self,news:dict):
        News(**news,company = self.__targetCompany).save()

    def __stripDetail(self, obj, key, value):
        try:
            obj[key] = value().get_text().strip().replace(r"(?:  |\n)", "")
        except AttributeError:
            obj[key] = ""

    def __getLinks(self, URL: str, links=[], page=1) -> None:
        print(URL + f"&pageno={page}")
        response = requests.get(URL + f"&pageno={page}")
        soup = BeautifulSoup(response.content.decode("utf-8", "ignore"), self.PARSER)
        currentPageLinks = soup.find_all(
            "a",
            href=re.compile(r"^/news/(?:results|recommendations|business)/.*[.]html$"),
        )
        #converting the currentPageLink to only hold the URLS (string ) insted of the BeautifulSoup obj
        currentPageLinks = [link['href'] for link in currentPageLinks if link.get_text()]
        # return links
        if currentPageLinks:
            asyncio.run(self.__concurrent(currentPageLinks))
            return self.__getLinks(
                URL=URL,
                links=links,
                page=page + 1,
            )
        return None
    
    async def __concurrent(self,links:str) -> list[dict]:
        loop  = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await asyncio.gather(*[loop.run_in_executor(executor, self.__getPage, link) for link in links])

    def __getPage(self, URL:str) -> None:
        print(self.BASE_URL + URL)
        newsPage = BeautifulSoup(
            requests.get(self.BASE_URL + URL).content.decode(
                "utf-8", "ignore"
            ),
            self.PARSER,
        )
        self.__getPageData(newsPage,self.BASE_URL + URL)
    
    def __getPageData(self, Page:BeautifulSoup(), pageURL:str) -> None:
        obj = {}
        obj["source"] = pageURL

        self.__stripDetail(
            obj, "title", lambda: Page.select_one(".article_title")
        )
        
        if not obj['title']: return None

        self.__stripDetail(
            obj, "description", lambda: Page.select_one(".article_desc")
        )
        self.__stripDetail(
            obj, "author", lambda: Page.select_one(".article_author")
        )

        self.__stripDetail(
            obj, "scheduled", lambda: Page.select_one(".article_schedule")
        )
        # obj['scheduled'] = timezone.now()
        obj['scheduled'] = dateutil.parser.parse(obj["scheduled"]).replace(tzinfo=dateutil.tz.gettz('Asia/Kolkata')) if obj["scheduled"] else None
        
        content = []
        isLastParaCrossed = False
        paraList = []

        try:
            paraList += Page.select_one("#contentdata").find_all("p")
        except AttributeError:
            pass
            # warnings.warn(f"couldn't get the content of \n {pageURL}")

        try:
            paraList += Page.find(
                "div", attrs={"itemprop": "articleBody"}
            ).find_all("p")
        except AttributeError:
            pass

        if not paraList:    warnings.warn(f"context not found {pageURL}")
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
        
        self.__saveNews(obj)
        self.__pagesData = self.__pagesData + [obj]
        # return obj

    def main(
        self,
        SYMBOL: str = "RI",
        DURATION: str = 1,
        DURATION_TYPE: str = "M",
        YEAR: str = timezone.now().year,
    ) -> list[dict]:
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
        self.__getLinks(URL=URL, links=[])
        print("____COMPLETE____")
        return None


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
    scraper.setTargetCompany(target_company)
    scraper.main(
        SYMBOL=target_company.symbol, DURATION_TYPE=input("Type [M]: ")
    )