from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from pathlib import Path
import mimetypes
from os import makedirs
from time import sleep
import pandas as pd

MIME_TYPES = ";".join(mimetypes.types_map.values())
DT_REF = datetime.now()
PATH_DOWNLOAD = (
    Path() / "download" /
    f"{DT_REF.day:02d}{DT_REF.month:02d}{DT_REF.year}"
)


def esperar_tag(driver: WebDriver, by: By, tag: str, timeout: float = 30.0) -> None:
    element = (
        WebDriverWait(driver=driver, timeout=timeout)
        .until(
            EC.presence_of_element_located(
                (by, tag)
            )
        )
    )

    return element


def nav_login(driver: WebDriver, login: str, senha: str) -> None:
    id_tags = [
        ("UserName", login),
        ("Password", senha),
        ("newLogonButton", None)
    ]

    for tag, text in id_tags:
        action_tag = esperar_tag(driver, By.ID, tag)
        if text is not None:
            action_tag.send_keys(text)
        else:
            action_tag.click()


def nav_single_store(driver: WebDriver) -> None:
    # TODO -> CLICAR NO LINK REPORT
    nav_tags = [
        ("rptAnchor", By.ID),
        ("id_8", By.ID),
        ("//li[@data-rptname='DPR_SINGLE_STORE']", By.XPATH)
    ]

    for tag, byby in nav_tags:
        action_tag = esperar_tag(driver, byby, tag)
        action_tag.click()


def nav_single_periodo(driver: WebDriver, per_date: datetime, seletores: Select, dias: int = 7) -> None:
    tags = [('from', 'rptFromDateDiv'), ('to', 'rptToDateDiv')]

    for dia in range(0, dias):
        dt_ref = (per_date + relativedelta(days=dia)).strftime('%B %d, %Y')

        for tag, img in tags:
            
            img = esperar_tag(driver, By.CSS_SELECTOR, f"#{img} img")
            ActionChains(driver).click(img).perform()

            sleep(2.0)
            
            action_tag = esperar_tag(driver, By.ID, tag)
            action_tag.clear()
            action_tag.send_keys(dt_ref)
        

        for op in seletores.options:
            op.click()

            sleep(3.0)

            download(driver)

    sleep(6.0)

    df = tratamento_arquivos()
    df.to_excel('BASE.xlsx', index=False)


def nav_single_lojas(driver: WebDriver, by: By, tag: str) -> Select:
    elm = esperar_tag(driver, by, tag)
    seletores = Select(elm)

    return seletores


def download(driver: WebDriver):
    tags = [
        ('rptRunDownloadBtn', By.ID),
        ('DownloadCSV', By.ID),
    ]

    for tag, byby in tags:
        action_tag = esperar_tag(driver, byby, tag)
        action_tag.click()

    while True:
        is_visible = driver.find_element(tags[0][1], tags[0][0]).is_displayed()

        if is_visible:
            break

        sleep(2.0)


def tratamento_arquivos():
    return (
        pd.concat(
            [
                pd.read_csv(c)
                for c in PATH_DOWNLOAD.glob("**/*.csv")
                if c.stat().st_size > 0
            ]
        )
        .loc[
            :,
            lambda _df: ~_df.columns.str.match('Unnamed')
        ]
        .drop_duplicates(subset=['End Date', 'Store'])
    )


def main_spider(init_date: str, days: int, login: str
              , password: str, url: str, invisible: bool = False) -> None:
              
    if not PATH_DOWNLOAD.is_dir():
        makedirs(PATH_DOWNLOAD)

    service = FirefoxService(executable_path=GeckoDriverManager().install())
    options = FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", str(PATH_DOWNLOAD.absolute()))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", MIME_TYPES)
    options.headless = invisible

    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url = url)
    driver.implicitly_wait(30)

    nav_login(driver, login, password)

    nav_single_store(driver)

    lojas = nav_single_lojas(driver, By.ID, "storesDD")
    nav_single_periodo(driver, parse(init_date), lojas, days)
