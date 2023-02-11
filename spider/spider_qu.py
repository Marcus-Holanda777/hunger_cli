import mimetypes
from pathlib import Path
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from time import sleep
from random import randint
from dataclasses import dataclass
from datetime import datetime
from openpyxl import load_workbook
import pandas as pd

# interacao com o teclado e mouse
from selenium.webdriver import ActionChains, Keys

# esperar a tag aparecer
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LIMIT_DAY = 31

MIME_TYPES = ";".join(mimetypes.types_map.values())
DT_REF = datetime.now()
PATH_DOWNLOAD = (
    Path() / "download_qu" /
    f"{DT_REF.day:02d}{DT_REF.month:02d}{DT_REF.year}"
)


@dataclass()
class Navegacao:
    by: By
    tag: str
    send_text: str = None
    btn: bool = False


class SpiderQu:
    def __init__(self, url: str, 
                       implicitly_wait: float, 
                       login: str, 
                       password: str, 
                       date_start: datetime, 
                       date_end: datetime,
                       invisible: bool = False) -> None:
        self.url = url
        self.implicitly_wait = implicitly_wait
        self.user = login
        self.password = password
        self.date_start = date_start
        self.date_end = date_end
        self.invisible = invisible
        self.options = self.__options()
        self.service = FirefoxService(executable_path=GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=self.service, options=self.options)


    def __options(self):
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
                action_tag.send_keys(tag.send_text)
            else:
                action_tag.click()


    def delay(self, start: int, end: int) -> None:
        espera =  randint(start, end)
        sleep(float(espera))
    

    def get_url(self) -> None:
        self.driver.get(self.url)
    

    def login(self) -> None:
        tags = [
            Navegacao(by=By.CSS_SELECTOR, tag="input[name='username']", send_text=self.user), 
            Navegacao(by=By.CSS_SELECTOR, tag="input[name='password']", send_text=self.password),
            Navegacao(by=By.CSS_SELECTOR, tag="button[name='login-btn']", btn=True)
        ]

        self.navegar(tags=tags)
        self.esperar_tag(By.XPATH, "//span[contains(text(), 'Close')]")
        
        escape = ActionChains(self.driver).send_keys(Keys.ESCAPE)
        escape.perform()

        self.delay(2, 4)

    
    def relatorio(self):
        tags = [
            Navegacao(by=By.PARTIAL_LINK_TEXT, tag="Reports", btn=True),
            Navegacao(by=By.XPATH, tag="//span[contains(text(), 'Summary By Date')]", btn=True)
        ]

        self.navegar(tags=tags)
        self.delay(2, 4)
    

    def date_from_to(self):
        # TODO: LOCALIZAR A LABEL FROM
        tags = ('From', 'To')

        for tag_label in tags:
            tbl_from = (
                self.esperar_tag(By.XPATH, f"//label[normalize-space(text())='{tag_label}']")
                 .find_element(By.XPATH, "..")
            )

            if tag_label == 'From':
                date_ref = self.date_start
            else:
                date_ref = self.date_end

            # TODO: Filtro YEAR
            elm_year = tbl_from.find_element(By.CSS_SELECTOR, f"option[value='{str(date_ref.year)}']").find_element(By.XPATH, "..")
            sel_year = Select(elm_year)
            sel_year.select_by_value(str(date_ref.year))

            # TODO: Filtro MONTHY
            elm_month = tbl_from.find_element(By.CSS_SELECTOR, f"option[value='{str(date_ref.month - 1)}']").find_element(By.XPATH, "..")
            sel_month = Select(elm_month)
            sel_month.select_by_value(str(date_ref.month - 1))

            # TODO: Filtro DAY
            elm_day = tbl_from.find_element(By.LINK_TEXT, str(date_ref.day))
            elm_day.click()

            self.delay(2, 4)
        
        btn_sucess = self.esperar_tag(By.XPATH, "//button[@class='button is-success']")
        btn_sucess.click()


    def store_list(self) -> list[str]:
        # TODO: Botao para mostra a lista
        btn_list = self.esperar_tag(By.XPATH, "//input[@value='store-list']")
        ActionChains(self.driver).click(btn_list).perform()

        # TODO: Botao que mostra a lista de lojas
        self.btn_danger().click()
        self.delay(2, 4)

        # TODO: Capturar lista de lojas
        list_store = self.esperar_tag(By.XPATH, "//a[contains(@class,'dropdown-item')]", all=True)
        all_link = [
            link.text for link in list_store
        ]

        # TODO: Excluir loja da lista
        return all_link
        

    def espera_download(self):
        original = self.driver.current_window_handle

        while True:
            is_visible = (
                WebDriverWait(self.driver, 30.0, 1.0)
                 .until_not(
                   EC.presence_of_element_located((By.XPATH, "//div[@class='modal-background']"))
                 )
            )

            is_quias = len(self.driver.window_handles) == 1

            if is_visible and is_quias:
                break

            sleep(2.0)
        
        self.driver.switch_to.window(original)
    

    def btn_danger(self):
        return (
            self.esperar_tag(By.XPATH, "//input[@placeholder='Select Store']")
        )


    def btn_export(self):
        return (
             self.esperar_tag(
                By.XPATH, 
                "//button[@class='button is-light']//span[normalize-space(text())='Export']"
            )
        )
    

    def btn_download(self):
        return (
            self.esperar_tag(
                By.XPATH, 
                "//button[@class='button is-light']//span[normalize-space(text())='Download File']"
            )
        )
            

    def download(self, all_link: list[str]) -> None:
        for link in all_link:
            self.btn_danger().click()
            
            self.delay(2, 4)
            self.esperar_tag(By.LINK_TEXT, link).click()
            
            self.btn_export().click()
            self.btn_download().click()

            self.espera_download()
            self.esperar_tag(By.XPATH, "//a[@class='tag is-delete']").click()


    def filtros(self):

        filtro = self.esperar_tag(By.CSS_SELECTOR, "strong[data-msgid='Show Filters']")
        filtro.click()

        selm = self.esperar_tag(By.TAG_NAME, "select")
        
        list_sel = Select(selm)
        list_sel.select_by_value('range')
        
        # TODO: Definir intervalo de datas, para filtrar relatorio
        intervalo = self.esperar_tag(By.CSS_SELECTOR, "button[class='button is-info']")
        intervalo.click()
        
        self.delay(2, 4)
        self.date_from_to()

        all_link = self.store_list()
        self.download(all_link=all_link)


    def tratamento_base(self, arq: Path):
        def name_location(arq: Path) -> str:
            wb = load_workbook(arq, read_only=True)
            ws = wb.active

            name = (
                ws.cell(6, 1)
                 .value
                 .split(':')[1]
                 .split(',')[0]
            )
            wb.close()

            return name
        
        def transform(df: pd.DataFrame) -> pd.DataFrame:
            return (
                pd
                  .melt(df, id_vars=['Section', 'Metric'], var_name="Date", value_name='Total')
                  .assign(Date = lambda _df: _df['Date'].map(pd.to_datetime), Location = name_location(arq))
              )
        
        not_total = "total"
        not_employees = "employees"

        return (
            pd
              .read_excel(arq, skiprows=7)
              .assign(Section = lambda _df: _df['Section'].fillna(method='ffill'))
              .iloc[:, :-1]
              .query("Metric.str.lower() != @not_total")
              .query("Section.str.lower() != @not_employees")
              .pipe(transform)
        )

    
    def concat_path(self):
        return ( 
            pd.concat(
                [
                    self.tratamento_base(arq)
                    for arq in PATH_DOWNLOAD.glob("**/*.xlsx")
                    if arq.stat().st_size > 0
                ]
            )
        )


    def close(self) -> None:
        self.driver.quit()
    

    def run(self) -> None:
        
        self.get_url()
        self.login()
        self.relatorio()
        self.filtros()
        self.close()

        self.delay(4,6)

        df = self.concat_path()
        df.to_excel('REPORT_QU.xlsx', index=False)
