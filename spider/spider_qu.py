import configparser
from pathlib import Path
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from time import sleep
from random import randint
from dataclasses import dataclass
from datetime import datetime

# interacao com o teclado e mouse
from selenium.webdriver import ActionChains, Keys

# esperar a tag aparecer
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ARQ_INIT = Path("c:\magoo\config.init")
config = configparser.ConfigParser()
config.read(ARQ_INIT)

login = config['SESSION_QU']['Login']
password = config['SESSION_QU']['Password']
url = config['SESSION_QU']['Url']


@dataclass()
class Navegacao:
    by: By
    tag: str
    send_text: str = None
    btn: bool = False


class SpiderQu:
    def __init__(self, url: str, implicitly_wait: float, 
                       login: str, password: str, 
                       date_start: datetime, date_end: datetime) -> None:
        self.url = url
        self.implicitly_wait = implicitly_wait
        self.user = login
        self.password = password
        self.date_start = date_start
        self.date_end = date_end
        self.service = FirefoxService(executable_path=GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=self.service)
    

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
    

    def date_from(self):
        tbl_from = self.esperar_tag(By.XPATH, "//div[@]")
        # TODO: Filtro YEAR
        elm_year = self.esperar_tag(By.CSS_SELECTOR, "option[value='2023']").find_element(By.XPATH, "..")
        sel_year = Select(elm_year)
        sel_year.select_by_value(str(self.date_start.year - 1))

        # TODO: Filtro MONTHY
        elm_month = self.esperar_tag(By.CSS_SELECTOR, "option[value='0']").find_element(By.XPATH, "..")
        sel_month = Select(elm_month)
        sel_month.select_by_value(str(self.date_start.month))

        # TODO: Filtro DAY
    

    def date_to(self):
        ...

    
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
        self.date_from()


    def close(self) -> None:
        self.driver.quit()
    

    def run(self) -> None:
        self.get_url()
        self.login()
        self.relatorio()
        self.filtros()
        # self.close()

# Existe uma tela spos o login, informando as mudanças na pagina
# solução simular o click do butão ESC para sai da pagina
# ou encontrar a tag de fechar o informativo

if __name__ == '__main__':
    SpiderQu(
        url=url, 
        implicitly_wait=30.0, 
        login=login, 
        password=password,
        date_start=datetime(2023, 2, 1),
        date_end=datetime(2023, 2, 7)
    ).run()
