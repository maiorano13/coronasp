from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import pyodbc
import pandas as pd
from datetime import datetime

conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-5HPPJ5N\SQLEXPRESS;'
                          'Database=Covid19;'
                          'Trusted_Connection=yes;')

dataset =  pd.read_sql("SELECT * FROM [dbo].[casos_doencas]", conn)
dataset = dataset.dropna()
features = dataset[["dia_inicio_sintomas", "municipio", "idade", "cs_sexo", "cardiopatia", "obesidade", "asma", "imunodepressao"]]
features["dia_inicio_sintomas"] = features["dia_inicio_sintomas"].apply(lambda x: x.replace("-", "") )
features["cs_sexo"] = features["dia_inicio_sintomas"].apply(lambda x: 0 if x == 'M' else 1 )

samples = dataset[["obito"]]

scaler = StandardScaler()
scaler.fit(features)
features = scaler.transform(features)
clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(4, 2), random_state=1)

clf.fit(features, samples)
##print(clf.predict_proba([[20200830, 3516200, 45, 0, 0, 0, 0, 0]]))
print("valor: ", clf.predict([[20200830, 3516200, 45, 0, 0, 0, 0, 0], [20200830, 3516200, 45, 0, 1, 1, 0, 0], 
[20200830, 3516200, 25, 1, 0, 0, 1, 1], [20200830, 3516200, 25, 0, 0, 0, 0, 0]]))

