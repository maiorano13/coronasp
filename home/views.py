import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
import pyodbc

conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-5HPPJ5N\SQLEXPRESS;'
                          'Database=Covid19;'
                          'Trusted_Connection=yes;')
print("conectou")

def home(request):
    
    datas = get_max_min_dates()
    cidades = get_municipios()
    
    return render(request, 'homepage.html', {'datas': datas,'cidades': cidades})

def get_max_min_dates():
    result = pd.read_sql("SELECT MAX([data]) AS [dt_max], MIN([data]) AS [dt_min] FROM [dbo].[data_semana]", conn)
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
            return HttpResponse(
                json.dumps({ 'success': 'true', 'data_casos_mortes': casos_mortes, 'data_idade': casos_idade, 'data_obitos_doencas': obitos_doencas
                }))
    return HttpResponse(
            json.dumps({ 'success': 'false'
            }))
    


def get_municipios():
    result = pd.read_sql("SELECT cod_ibge, nome_municipio FROM [dbo].[municipio]", conn)
    return result.to_dict('records')

def get_casos_idade(inicio, fim, municipio):
    sql = "SELECT idade, count(idade) AS casos FROM [dbo].[casos_doencas] WHERE idade is not null AND [dia_inicio_sintomas] BETWEEN ? AND ? "
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND [municipio] IN (?) '
        param.append(municipio)

    sql+= 'GROUP BY idade ORDER BY idade'
    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')

def get_casos_mortes_periodo_municipio(inicio, fim, municipio):
    sql= "SELECT [dia_inicio_sintomas] AS dia, COUNT(*) AS casos, SUM(CASE WHEN [obito] = 1 THEN 1 ELSE 0 END) AS obitos FROM [dbo].[casos_doencas] WHERE [dia_inicio_sintomas] BETWEEN ? AND ?"
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND [municipio] IN (?) '
        param.append(municipio)
    sql+= ' GROUP BY [dia_inicio_sintomas] ORDER BY [dia_inicio_sintomas] '
    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')

def get_obitos_doencas(inicio, fim, municipio):
    sql = "SELECT [asma], [cardiopatia], [diabetes], [doenca_hematologica], [doenca_hepatica]," \
            "[doenca_neurologica], [doenca_renal], [imunodepressao], [obesidade]," \
            "[outros_fatores_de_risco], [pneumopatia], [puerpera], [sindrome_de_down] " \
         "FROM [casos_doencas]" \
         "WHERE [obito] = 1 AND [dia_inicio_sintomas] BETWEEN ? AND ? "
	
    param=[inicio, fim]
    if(len(municipio)>0):
        sql+=' AND [municipio] IN (?) '
        param.append(municipio)

    result = pd.read_sql(sql, params=param, con=conn)
    return result.to_dict('records')