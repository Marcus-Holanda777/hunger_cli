from utils.parsexml import ParseXml

# manager do driver firefox e webdriver
from selenium import webdriver

# servico e cinfiguracao do driver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# selecionar tags
from selenium.webdriver.common.by import By

# interacao com o teclado e mouse
from selenium.webdriver import ActionChains, Keys

# esperar a tag aparecer
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import mimetypes
from pathlib import Path
from dataclasses import dataclass
from random import randint
from time import sleep
from dateutil.relativedelta import relativedelta
from os import makedirs
import pandas as pd


MIME_TYPES = ";".join(mimetypes.types_map.values())
DT_REF = datetime.now()
PATH_DOWNLOAD = (
    Path() / "download_sales" /
    f"{DT_REF.day:02d}{DT_REF.month:02d}{DT_REF.year}"
)


@dataclass
class Navegacao:
    by: By
    tag: str
    send_text: str = None
    btn: bool = False
    action: bool = False


class SpiderSales:
    def __init__(self, url: str, 
                       implicitly_wait: float, 
                       login: str, 
                       password: str, 
                       date_start: datetime, 
                       periodo: int,
                       invisible: bool = False) -> None:
        self.url = url
        self.implicitly_wait = implicitly_wait
        self.user = login
        self.password = password
        self.date_start = date_start
        self.periodo = periodo
        self.invisible = invisible
        self.options = self.__options()
        self.driver = webdriver.Firefox(options=self.options)
    

    def __options(self):

        if not PATH_DOWNLOAD.is_dir():
            makedirs(PATH_DOWNLOAD)

        options = FirefoxOptions()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", str(PATH_DOWNLOAD.absolute()))
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", MIME_TYPES)
        options.headless = self.invisible

        return options
    

    def esperar_tag(self, by: By, tag: str, timeout: float = 30.0, all: bool = False) -> None:
        if not all:

            element = (
                WebDriverWait(driver=self.driver, timeout=timeout)
                .until(
                    EC.presence_of_element_located(
                        (by, tag)
                    )
                )
            )

        else:

            element = (
                WebDriverWait(driver=self.driver, timeout=timeout)
                .until(
                    EC.presence_of_all_elements_located(
                        (by, tag)
                    )
                )
            )


        return element
    

    def navegar(self, tags: list[Navegacao]) -> None:
        for tag in tags:
            action_tag = self.esperar_tag(tag.by, tag.tag)

            if not tag.btn:
                action_tag.clear()
                action_tag.send_keys(tag.send_text)
            else:
                if tag.action:
                    ActionChains(self.driver).click(action_tag).perform()
                else:
                    action_tag.click()
    

    def delay(self, start: int, end: int) -> None:
        espera =  randint(start, end)
        sleep(float(espera))
    

    def get_url(self) -> None:
        self.driver.get(self.url)
    
    
    def close(self) -> None:
        self.driver.quit()


    def login(self):
        tags = [
            Navegacao(by=By.ID, tag="UserName", send_text=self.user),
            Navegacao(by=By.ID, tag="Password", send_text=self.password),
            Navegacao(by=By.ID, tag="newLogonButton", btn=True)
        ]

        self.navegar(tags)
        self.delay(2, 4)


    def relatorio(self):
        tags = [
            Navegacao(by=By.ID, tag="rptAnchor", btn=True),
            Navegacao(by=By.ID, tag="id_8", btn=True),
            Navegacao(by=By.XPATH, tag="//li[@data-rptname='SALES_BY_ORDER_TYPE']", btn=True)
        ]

        self.navegar(tags)

        self.delay(2.0, 4.0)
        
        # VOLTAR AO TOPO DA PAGINA
        tag = self.driver.find_element(By.ID, 'contentBody')
        tag.send_keys(Keys.HOME)

        self.delay(2.0, 4.0)

     

    def download(self):
        tags = [
            Navegacao(by=By.ID, tag='rptRunDownloadBtn', btn=True),
            Navegacao(by=By.ID, tag='btnxml', btn=True)
        ]

        self.navegar(tags)

        while True:
            quias = len(self.driver.window_handles)

            if quias == 1:
                break

            self.delay(2.0, 3.0)
    

    def filter_date(self, dt_ref: str):
        range_date = [
            ('from', 'rptFromDateDiv'),
            ('to', 'rptToDateDiv'),
        ]
        
        for tag, div in range_date:
            tags = [
                Navegacao(by=By.CSS_SELECTOR, tag=f'#{div} img', btn=True, action=True), 
                Navegacao(by=By.ID, tag=tag, send_text=dt_ref)
            ]

            self.navegar(tags)
            self.delay(2.0, 2.0)
        
       
    def loop_main(self):
        for dia in range(0, self.periodo):
            dt_ref = (self.date_start + relativedelta(days=dia)).strftime('%B %d, %Y')
            self.filter_date(dt_ref)

            self.download()


    def concat_path(self) -> pd.DataFrame:
        return ( 
            pd.concat(
                [
                    ParseXml(arq).run()
                    for arq in PATH_DOWNLOAD.glob("**/*.xml")
                    if arq.stat().st_size > 0
                ]
            )
        )

    

    def run(self):
        self.get_url()
        self.login()
        self.relatorio()
        self.loop_main()
        self.close()

        self.delay(2.0, 4.0)

        df = self.concat_path()
        df.to_excel('REPORT_SALES.xlsx', index=False)