import pandas as pd
import requests
import io
import pyodbc
import re 
import numpy as np
from zipfile import ZipFile
'''
Atualizações semanais pelo GitHub da Agência de estatísticas do Estado de São Paulo (SEADE)
https://github.com/seade-R/dados-covid-sp
'''
## Conectar com o banco
conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-5HPPJ5N\SQLEXPRESS;'
                          'Database=Covid19;'
                          'Trusted_Connection=yes;')
cursor = conn.cursor()
def inserir_dia_semana(df_dia_semana):
    for index, row in df_dia_semana.iterrows():
        cursor.execute(
            "IF NOT EXISTS(SELECT data FROM data_semana WHERE data = ?) INSERT INTO data_semana (data, semana_ep) values(?,?)",
            row.datahora, row.datahora, row.semana_epidem)
    cursor.commit()

def inserir_drs(df_drs):
    for index, row in df_drs.iterrows():
        cursor.execute(
            "IF EXISTS(SELECT cod_drs FROM drs WHERE cod_drs = ?) UPDATE drs SET nome_drs = ? WHERE cod_drs = ?"
            " ELSE INSERT INTO drs (cod_drs, nome_drs) VALUES(?,?)", row.cod_drs, row.nome_drs, row.cod_drs,
            row.cod_drs, row.nome_drs)
    cursor.commit()

def inserir_municipios(df_cidades):
    df_cidades['latitude'] = df_cidades['latitude'].apply(lambda x: x.replace(",", "."))
    df_cidades['longitude'] = df_cidades['longitude'].apply(lambda x: x.replace(",", "."))

    for index, row in df_cidades.iterrows():
        cursor.execute(
            "IF EXISTS(SELECT cod_ibge FROM municipio WHERE cod_ibge = ?) UPDATE municipio SET nome_municipio "
            "= ?, cod_drs = ?, pop = ?, pop60 = ?, latitude = ?, longitude = ? WHERE cod_ibge = ? ELSE INSERT "
            "INTO municipio (cod_ibge, nome_municipio, cod_drs, pop, pop60, latitude, longitude) VALUES(?,?,?,"
            "?,?,?,?)", row.codigo_ibge, row.nome_munic, row.cod_drs, row.populacao, row.pop_60, row.latitude,
            row.longitude, row.codigo_ibge, row.codigo_ibge, row.nome_munic, row.cod_drs, row.populacao, row.pop_60,
            row.latitude, row.longitude)
    cursor.commit()

def inserir_casos(df_covid_sp):
    for index, row in df_covid_sp.iterrows():
        cursor.execute("INSERT INTO covid_casos (dia, municipio_id, casos_novos, obitos_novos) values(?,?,?,?)",
                       row.datahora, row.codigo_ibge, row.casos_novos, row.obitos_novos)
    cursor.commit()

def inserir_casos_doencas(df_casos_doenca):
    df_casos_doenca = df_casos_doenca.replace({np.nan: None})
    df_casos_doenca['cs_sexo'] = df_casos_doenca['cs_sexo'].apply(lambda x: 'F' if x == 'FEMININO' else 'M')
    df_casos_doenca['diagnostico_covid19'] = df_casos_doenca['diagnostico_covid19'].apply(
        lambda x: 'TRUE' if x == 'CONFIRMADO' else 'FALSE')
    df_casos_doenca['obito'] = df_casos_doenca['obito'].apply(lambda x: 'FALSE' if x == 0 else 'TRUE')
    df_casos_doenca['asma'] = df_casos_doenca['asma'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['cardiopatia'] = df_casos_doenca['cardiopatia'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['diabetes'] = df_casos_doenca['diabetes'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['doenca_hematologica'] = df_casos_doenca['doenca_hematologica'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['doenca_hepatica'] = df_casos_doenca['doenca_hepatica'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['doenca_neurologica'] = df_casos_doenca['doenca_neurologica'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['doenca_renal'] = df_casos_doenca['doenca_renal'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['imunodepressao'] = df_casos_doenca['imunodepressao'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['obesidade'] = df_casos_doenca['obesidade'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['outros_fatores_de_risco'] = df_casos_doenca['outros_fatores_de_risco'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['pneumopatia'] = df_casos_doenca['pneumopatia'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['puerpera'] = df_casos_doenca['puerpera'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    df_casos_doenca['sindrome_de_down'] = df_casos_doenca['sindrome_de_down'].apply(
        lambda x: 'FALSE' if (x == 'IGNORADO' or x == 'NÃO') else 'TRUE')
    for index, row in df_casos_doenca.iterrows():
        cursor.execute("INSERT INTO casos_doencas (id, dia_inicio_sintomas, municipio, idade, cs_sexo, "
                       "diagnostico_covid19, obito, asma, cardiopatia, diabetes, doenca_hematologica, doenca_hepatica, "
                       "doenca_neurologica, doenca_renal, imunodepressao, obesidade, outros_fatores_de_risco, "
                       "pneumopatia, puerpera, sindrome_de_down) values(NEXT VALUE FOR casos_doencas_id,?,?,?,?,?,?,?,?,"
                       "?,?,?,?,?,?,?,?,?,?,?)", row.data_inicio_sintomas, row.codigo_ibge, row.idade, row.cs_sexo,
                       row.diagnostico_covid19, row.obito, row.asma, row.cardiopatia, row.diabetes,
                       row.doenca_hematologica,
                       row.doenca_hepatica, row.doenca_neurologica, row.doenca_renal, row.imunodepressao, row.obesidade,
                       row.outros_fatores_de_risco, row.pneumopatia, row.puerpera, row.sindrome_de_down)
    cursor.commit()

def inserir_internacoes(df_internacoes, df_drs):
    ## Descobrir o cod_drs -- Diferente do arquivo de dados_covid_sp
    cod_drs = []
    for index, row in df_internacoes.iterrows():
        nome_drs = 'Grande São Paulo' if (
                    row.nome_drs.find('São Paulo') != -1 or row.nome_drs.find('SP') != -1) else re.sub('\d', '',
                                                                                                       row.nome_drs).replace(
            'DRS', '').strip()
        cod_drs.append(df_drs.at[df_drs.index[df_drs['nome_drs'] == nome_drs].tolist()[0], 'cod_drs'])

    df_internacoes['cod_drs'] = cod_drs
    df_internacoes['pacientes_uti_mm7d'] = df_internacoes['pacientes_uti_mm7d'].apply(
        lambda x: float(x.replace(",", ".")))
    df_internacoes['total_covid_uti_mm7d'] = df_internacoes['total_covid_uti_mm7d'].apply(
        lambda x: float(x.replace(",", ".")))
    df_internacoes['ocupacao_leitos'] = df_internacoes['ocupacao_leitos'].apply(lambda x: float(x.replace(",", ".")))
    df_internacoes['leitos_pc'] = df_internacoes['leitos_pc'].apply(lambda x: float(x.replace(",", ".")))
    df_internacoes['internacoes_7v7'] = df_internacoes['internacoes_7v7'].apply(lambda x: float(x.replace(",", ".")))
    df_internacoes['ocupacao_leitos_ultimo_dia'] = df_internacoes['ocupacao_leitos_ultimo_dia'].apply(
        lambda x: float(x.replace(",", ".")))
    df_internacoes['pacientes_enf_mm7d'] = df_internacoes['pacientes_enf_mm7d'].apply(
        lambda x: float(x.replace(",", ".")))
    df_internacoes['total_covid_enf_mm7d'] = df_internacoes['total_covid_enf_mm7d'].apply(
        lambda x: float(x.replace(",", ".")))
    ## agrupar quando dia e cod_drs igual
    df_internacoes = df_internacoes.groupby(['datahora', 'cod_drs']).sum().reset_index().rename(
        columns={'pop': 'populacao'})

    for index, row in df_internacoes.iterrows():
        cursor.execute("INSERT INTO covid_internacoes ([dia], [drs], [pacientes_uti_ultimo_dia], "
                       "[total_covid_uti_ultimo_dia], [pacientes_uti_mm7d], [total_covid_uti_mm7d], [ocupacao_leitos], [pop], "
                       "[leitos_pc], [internacoes_7d], [internacoes7d_l], [internacoes7v7], [ocupacao_leitos_ultimo_dia], "
                       "[pacientes_enf_mm7d], [total_covid_enf_mm7d], [pacientes_enf_ultimo_dia], "
                       "[total_covid_enf_ultimo_dia], [internacoes_ultimo_dia]) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       row.datahora, row.cod_drs, row.pacientes_uti_ultimo_dia,
                       row.total_covid_uti_ultimo_dia, row.pacientes_uti_mm7d, row.total_covid_uti_mm7d,
                       row.ocupacao_leitos, row.populacao,
                       row.leitos_pc, row.internacoes_7d, row.internacoes_7d_l, row.internacoes_7v7,
                       row.ocupacao_leitos_ultimo_dia,
                       row.pacientes_enf_mm7d, row.total_covid_enf_mm7d, row.pacientes_enf_ultimo_dia,
                       row.total_covid_enf_ultimo_dia, row.internacoes_ultimo_dia)
    cursor.commit()


## dados_covid_sp
url = 'https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/dados_covid_sp.csv'
download = requests.get(url).content


df_covid_sp = pd.read_csv(io.StringIO(download.decode('utf-8')), ';')
df_covid_sp['codigo_ibge'] = df_covid_sp['codigo_ibge'].apply(lambda x: 3599999 if x == 9999999 else x)
print("Total registros dados_covid_sp: ", len(df_covid_sp))

# GET Dias e semanas ep
print('Inserir novas semanas epi')
df_dia_semana = df_covid_sp[['datahora', 'semana_epidem']].drop_duplicates(subset="datahora")
print("Total registros dia_semana: ", len(df_dia_semana))
inserir_dia_semana(df_dia_semana)
print('Semana Epi  Finalizado!')

# GET DRS
df_cidades = df_covid_sp[['datahora', 'codigo_ibge', 'nome_munic', 'cod_drs','nome_drs', 'nome_ra', 'cod_ra', 'pop', 'pop_60','latitude', 'longitude']].sort_values(by='datahora', ascending=False).drop_duplicates(subset="codigo_ibge").dropna().reset_index().rename(columns={'pop':'populacao'})
df_drs = df_cidades[['datahora', 'cod_drs', 'nome_drs']].sort_values(by='datahora', ascending=False).drop_duplicates(subset="cod_drs").reset_index()

'''
print('Inserir DRS (somente primeira execução)')
print("Total registros drs: ", len(df_drs))
inserir_drs(df_drs)
print('DRS  Finalizado!')
'''

# GET municipios
'''
print('Inserir Cidades (somente primeira execução)')
print("Total registros cidades: ", len(df_cidades))
inserir_municipios(df_cidades)
print('Cidades  Finalizado!')
'''

## GET Casos/Obitos

print('Inserir Casos_Obitos novos')
cursor.execute('SELECT MAX(dia) FROM covid_casos')
max_day = cursor.fetchone()[0]
print('Dados até: ', max_day)
df_covid_sp = df_covid_sp[df_covid_sp.datahora > max_day]
print("Total registros covid_casos: ", len(df_covid_sp))
inserir_casos(df_covid_sp)
print('Casos/Obitos  Finalizado!')

'''
#### Casos doenças preexistentes
print('Inserir Casos_Doenças novos')
url = 'https://github.com/seade-R/dados-covid-sp/blob/master/data/casos_obitos_doencas_preexistentes.csv.zip?raw=true'
download = requests.get(url).content
zipfile = ZipFile(io.BytesIO(download))
df_casos_doenca = pd.read_csv(zipfile.open('casos_obitos_doencas_preexistentes.csv'), ';')
print("Total registros casos doenças: ", len(df_casos_doenca))
inserir_casos_doencas(df_casos_doenca)
print('Casos/Doenças  Finalizado!')

#### Casos raça
url = 'https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/casos_obitos_raca_cor.csv.zip'
download = requests.get(url).content
zipfile = ZipFile(io.BytesIO(download))
df_casos_raca = pd.read_csv(zipfile.open('casos_obitos_raca_cor.csv'), ';')
df_casos_raca = df_casos_raca.replace({np.nan: None})
df_casos_raca['codigo_ibge'] = df_casos_raca['codigo_ibge'].fillna('3599999') ## casos onde cidade é nula fill com ignorado
df_casos_raca['raca_cor'] = df_casos_raca['raca_cor'].fillna('IGNORADO')
df_casos_raca['raca_cor'] = df_casos_raca['raca_cor'].replace({'NONE': 'IGNORADO'})
df_casos_raca['cs_sexo'] = df_casos_raca['cs_sexo'].apply(lambda x: 'F' if x == 'FEMININO' else 'M')
df_casos_raca['obito'] = df_casos_raca['obito'].apply(lambda x: 'FALSE' if x == 0 else 'TRUE')
print("Total registros casos raça: ", len(df_casos_raca))
cursor.execute("TRUNCATE TABLE casos_cor_raca")
for index, row in df_casos_raca.iterrows():
    print(index)
    cursor.execute("INSERT INTO casos_cor_raca (municipio, obito, raca_cor, sexo, idade) values(?,?,?,?,?)",
                    int(row.codigo_ibge), row.obito, row.raca_cor, row.cs_sexo, row.idade)

cursor.commit()
print('Casos/Raça Finalizado!')
'''

# internações
'''
print('Internações série antiga (Primeira vez somente)')
url = "https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/plano_sp_leitos_internacoes.csv"
download = requests.get(url).content
df_internacoes = pd.read_csv(io.StringIO(download.decode('utf-8')), ';')
df_internacoes = df_internacoes[df_internacoes.datahora < '2020-10-08']
df_internacoes = df_internacoes[df_internacoes.nome_drs != 'Estado de São Paulo']

print("Total registros internações serie antiga: ", len(df_internacoes))

inserir_internacoes(df_internacoes, df_drs)
print('Internações série antiga Completo')
'''
print('Internações série nova')
# Get ultimo dia de registo de internações
cursor.execute('SELECT MAX(dia) FROM covid_internacoes')
max_day = cursor.fetchone()[0]
print('Dados até: ', max_day)
print('Internações série antiga (Primeira vez somente)')
url = "https://raw.githubusercontent.com/seade-R/dados-covid-sp/master/data/plano_sp_leitos_internacoes_serie_nova_variacao_semanal.csv"
download = requests.get(url).content
df_internacoes = pd.read_csv(io.StringIO(download.decode('utf-8')), ';')
df_internacoes = df_internacoes[df_internacoes.datahora > max_day]
df_internacoes = df_internacoes[df_internacoes.nome_drs != 'Estado de São Paulo']

print("Total registros internações serie nova: ", len(df_internacoes))

inserir_internacoes(df_internacoes, df_drs)
print('Internações série nova Completo')


