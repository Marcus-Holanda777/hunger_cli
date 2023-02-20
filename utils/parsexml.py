from pathlib import Path
from lxml import etree
import string
import re
import pandas as pd
import numpy as np


class ParseXml:
    def __init__(self, caminho: Path, ns = '{urn:crystal-reports:schemas:report-detail}') -> None:
        self.caminho = caminho
        self.ns = ns
        self.root = self.__get_root()
        self.data = []


    def format_text(self, text):
        text = re.sub(r'\n|/', ' ', text)
        text = [c for c in
            [
                w.strip(string.punctuation+string.whitespace)
                for w in text.split(' ')
            ]
            if c != ''
        ]

        return ' '.join(text)


    def __get_root(self):
        tree = etree.parse(self.caminho)
        root = tree.getroot()
        
        for doc in root.iter():
            doc.tag = doc.tag[len(self.ns):]
        return root


    def set_periodo(self):
        self.periodo = (
            self.root.find('ReportHeader/Section/Field[@Name="EndDate1"]/Value')
            .text[:10]
        )
    

    def set_store(self, elm):
        self.store = elm.find('.//Value').text
    

    def set_columns(self, elm):
        self.columns = [self.format_text(c) for c in elm.xpath("Group[@Level='2']//TextValue/text()")]
        self.columns.insert(0, 'Store Name')
        self.columns.insert(1, 'Date')
    

    def set_values(self, elm):
        self.values = elm.xpath(".//Value/text()")
        self.values.insert(0, self.store)
        self.values.insert(1, self.periodo)

    
    def etl_xml(self):
        def convert_type(df: pd.DataFrame) -> pd.DataFrame:
            df[df.columns[3:]] = df[df.columns[3:]].astype('float')
            return df

        return (
            pd.DataFrame(self.data)
             .astype({'Date': np.datetime64})
             .pipe(convert_type)
        )


    def run(self):
        self.set_periodo()
        
        for elm in self.root.xpath("//Group[@Level='1']"):
            # TODO: Retornar o nome da filial
            self.set_store(elm)

            #TODO: Retornar nome das colunas
            self.set_columns(elm)

            # TODO: Retornar os valores
            for value in elm.xpath(".//Details[@Level='3']"):
                self.set_values(value)

                add = dict(zip(self.columns, self.values))
                self.data.append(add)
        
        return self.etl_xml()