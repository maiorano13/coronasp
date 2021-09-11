from datetime import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
import psycopg2
import locale

'''conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-5HPPJ5N\SQLEXPRESS;'
                          'Database=Covid19;'
                          'Trusted_Connection=yes;')

'''
conn=psycopg2.connect(host="localhost",
                        port="5432",
                        user="postgres",
                        password="webpro33",
                        database="covidsp")
print("Connected!")
cursor = conn.cursor()

def home(request):
    
    datas = get_max_min_dates()
    cidades = get_municipios()
    
    return render(request, 'homepage.html', {'datas': datas,'cidades': cidades})

def get_max_min_dates():
    result = pd.read_sql("SELECT MAX(data) AS dt_max, MIN(data) AS dt_min FROM data_semana", conn)
    result['dt_max'] = result['dt_max'].apply(lambda x: x.strftime("%Y-%m-%d"))
    result['dt_min'] = result['dt_min'].apply(lambda x: x.strftime("%Y-%m-%d"))

    return result.to_dict('records')

def filtrar(request):
    if request.method == 'POST':
        date_start = request.POST.get('date_start')
        date_end = request.POST.get('date_end')
        cidade =  request.POST.get('cidade')
        validado = True

        if len(date_start)  == 0:
            validado = False

        if len(date_end)  == 0:
            validado = False

        if len(cidade)  == 0:
            validado = False 

        if validado: 
            if int(cidade) == 0:
                cidade = ''

            casos_idade = get_casos_idade(date_start, date_end, cidade)
            casos_mortes = get_casos_mortes_periodo_municipio(date_start, date_end, cidade)
            obitos_doencas = get_obitos_doencas(date_start, date_end, cidade)
            vacina_evolucao = get_vacina_evolucao()
            qtdes = get_qtde_casos_obitos(date_start, date_end, cidade)
            ##print(casos_idade)
            return HttpResponse(
                json.dumps({ 'success': 'true', 'data_casos_mortes': casos_mortes, 'data_idade': casos_idade, 'data_obitos_doencas': obitos_doencas,
                'data_vacina_evolucao': vacina_evolucao, 'qtdes': qtdes, 
                }, default=str))
    return HttpResponse(
            json.dumps({ 'success': 'false'
            }))
    


def get_municipios():
    result = pd.read_sql("SELECT cod_ibge, nome_municipio FROM municipio ORDER BY nome_municipio", conn)
    return result.to_dict('records')


def get_qtde_casos_obitos(inicio, fim, municipio):
    sql = "SELECT COUNT(*) AS casos, SUM(CASE WHEN obito IS TRUE THEN 1 ELSE 0 END) AS obitos FROM casos_doencas WHERE dia_inicio_sintomas BETWEEN %s AND %s "
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND municipio IN (%s) '
        param.append(municipio)

    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')
    
    

def get_casos_idade(inicio, fim, municipio):
    sql = "SELECT idade, count(idade) AS casos FROM casos_doencas WHERE idade is not null AND dia_inicio_sintomas BETWEEN %s AND %s "
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND municipio IN (%s) '
        param.append(municipio)

    sql+= 'GROUP BY idade ORDER BY idade'
    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')

def get_casos_mortes_periodo_municipio(inicio, fim, municipio):
    sql= "SELECT dia_inicio_sintomas AS dia, COUNT(*) AS casos, SUM(CASE WHEN obito IS TRUE THEN 1 ELSE 0 END) AS obitos FROM casos_doencas WHERE dia_inicio_sintomas BETWEEN %s AND %s"
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND municipio IN (%s) '
        param.append(municipio)
    sql+= ' GROUP BY dia_inicio_sintomas ORDER BY dia_inicio_sintomas '
    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')

def get_obitos_doencas(inicio, fim, municipio):
    sql = "SELECT asma, cardiopatia, diabetes, doenca_hematologica, doenca_hepatica," \
            "doenca_neurologica, doenca_renal, imunodepressao, obesidade," \
            "outros_fatores_de_risco, pneumopatia, puerpera, sindrome_de_down " \
         "FROM casos_doencas" \
         " WHERE obito IS TRUE AND dia_inicio_sintomas BETWEEN %s AND %s "
	
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND municipio IN (%s) '
        param.append(municipio)

    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')

def get_vacina_evolucao():
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    
    df = pd.read_csv(r"home\templates\files\20210825_evolucao_aplicacao_doses.csv", sep=";")
    df['Dia de Data Registro Vacina'] = df['Dia de Data Registro Vacina'].apply(lambda x:  datetime.strptime(x, "%d de %B de %Y").date())
    df_total = df[df['Dose'] == ('2° DOSE' or 'UNICA')]
    df_total = df_total.rename(columns={'Contagem de Dose': 'totalmente_dose'})

    df_primeira = df[df['Dose'] == '1° DOSE']
    df_primeira = df_primeira.rename(columns={'Contagem de Dose': 'primeira_dose'})

    df = df.groupby('Dia de Data Registro Vacina').sum().reset_index()
    vacinas = pd.merge(df,df_total, on='Dia de Data Registro Vacina', how="left")
    vacinas = pd.merge(vacinas,df_primeira, on='Dia de Data Registro Vacina', how="left")
    vacinas = vacinas.fillna(0).rename(columns={'Dia de Data Registro Vacina': 'dia', "Contagem de Dose": "doses"})
    vacinas["dia"] = vacinas["dia"].apply(lambda x: x.strftime("%Y-%m-%d"))
    #index_names = df[df["Dose"] == 'UNICA'].index
    #df.drop(index_names, inplace = True)

    vacinas = vacinas[["dia", "doses", "totalmente_dose", "primeira_dose"]]  
    return vacinas.to_dict('records')