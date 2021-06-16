import json

from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
import pyodbc

def home(request):
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-5HPPJ5N\SQLEXPRESS;'
                          'Database=Covid19;'
                          'Trusted_Connection=yes;')
    print("conectou")
    result = pd.read_sql("SELECT idade as Country, count(idade) as Value FROM [dbo].[casos_doencas] WHERE idade is not null group by idade order by idade", conn)
    print(result, type)
    result = result.to_dict('records')
    print(result)
    c = ['United States', 'Russia', 'Germany (FRG)', 'France']
    v = [12394, 6148, 1653, 2162]
    cv = pd.DataFrame({'Country': c, 'Value': v})
    operacao = cv.to_dict('records')

    operacao.append({'columns': ['Country', 'Value']})
    #print(operacao)
    return render(request, 'homepage.html', {'json': result})