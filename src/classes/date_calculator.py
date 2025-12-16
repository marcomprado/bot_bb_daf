# Classe responsável por calcular as datas necessárias para as consultas

from datetime import datetime
from dateutil.relativedelta import relativedelta


class DateCalculator:
    # Classe responsável por calcular as datas inicial e final para as consultas
    
    def __init__(self):
        # Inicializa o calculador de datas
        self.data_atual = datetime.now()
    
    def calcular_data_inicial(self):
        # Calcula a data inicial (exatamente um mês antes da data atual)
        data_inicial = self.data_atual - relativedelta(months=1)
        return data_inicial.strftime("%d/%m/%Y")
    
    def calcular_data_final(self):
        # Calcula a data final (data atual)
        return self.data_atual.strftime("%d/%m/%Y")
    
    def obter_datas_formatadas(self):
        # Obtém ambas as datas formatadas de uma só vez
        data_inicial = self.calcular_data_inicial()
        data_final = self.calcular_data_final()
        
        print(f"Período: {data_inicial} até {data_final}")
        
        return data_inicial, data_final 