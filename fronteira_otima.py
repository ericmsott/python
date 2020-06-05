#from sgs import SGS, series
import pandas as pd
import matplotlib.pyplot as plt
import seaborn; seaborn.set(style = 'ticks')
import numpy as np
from pandas_datareader import data
# Abaixo define-se as datas dos dados:
start = "2020-02-21"
end = "2020-06-05"
# Abaixo define-se as acoes a serem baixadas (procure por outros tickers em: https://finance.yahoo.com/quote/%5EBVSP/components?p=%5EBVSP):
tickers = {'itau':'ITSA4.SA',
		'btgpactual':'BPAC11.SA',
		'viavarejo':'VVAR3.SA',
		'burguerking':'BKBR3.SA',
		'pdeacucar':'PCAR4.SA',
		'raiadsil':'RADL3.SA',
		'engie':'EGIE3.SA',
		'hapvida':'HAPV3.SA',
		'renner':'LREN3.SA',
		'americanas':'LAME3.SA'}
# Cria um dataframe vazio, contendo apenas as datas definidas:
stocks = pd.DataFrame(index=pd.date_range(start=start,end=end,freq="B"))

# O loop abaixo faz o download das series das acoes no yahoo finance:
for i in tickers: # para cada acao ...
	# cria uma serie (ATIVO = nome da acao; TICKER = codigo da acao; START e END = datas definidas no inicio do codigo):
	exec('{ATIVO}=data.DataReader("{TICKER}",data_source = "yahoo", start = "{START}", end = "{END}")'.format(ATIVO=i, TICKER=tickers[i], START = start, END = end))
	# Atribui uma nova coluna no dataframe vazio criado anteriormente para cada acao:
	exec('stocks["{ATIVO}"]={ATIVO}["Close"]'.format(ATIVO=i)) # (ATIVO = nome da acao)

#O comando abaixo eh necessario para remover valores ausentes (em feriados):
stocks = stocks.dropna() # Remove os NaNs

#stocks.to_csv(' inserir diretorio aqui !!!!') # Comando opcional para salvar o dataframe em um .csv

# calcula os retornos diarios de cada acao
retornos_diarios = stocks.pct_change()
# anualiza a media dos retornos acima
retornos_anuais = retornos_diarios.mean()*252
#matriz de covariancia dos retornos diarios
cov_diaria = retornos_diarios.cov()
#matriz de covariancia anualizada
cov_anual = cov_diaria*252

####### Agora Iremos simular 50000 portfolios para obter a fronteira eficiente #########

#       Listas Vazias para guardar os retornos, volatilidade e os pesos de cada acao.

port_retornos = [] #retornos dos portfolios
port_vol = []      #volatilidade dos portfolios
acoes_pesos = []   #pesos

#       O numero de simulacoes sera definido abaixo

num_acoes = len(tickers) #   numero de acoes
num_portfolios = 50000   #   numero de portfolios (recomendavel nao aumentar muito, pode pesar o computador)
# np.random.seed(300)    #   Comando opcional Garante que sempre ira gerar os mesmos numeros

#       O loop abaixo Preenche cada lista vazia com retornos de portfolios, risco e pesos das acoes

for portfolio in range(num_portfolios): #     Para cada portfolio dentre os 50.000 ...
	pesos = np.random.random(num_acoes) # ... cria um vetor aleatorio de tamanho = num_acoes
	#                                         para cada um desses vetores aleatorios estabeleceremos uma porcentagem de participacao no portfolio
	pesos /= np.sum(pesos) #                  equivalente a weights = weights/np.sum(weigths)
	retornos = np.dot(pesos, retornos_anuais)#multiplica cada retorno anual pelo seu respectivo peso atribuido e soma todos
	vol = np.sqrt(np.dot(pesos.T, np.dot(cov_anual,pesos))) # calcula a volatilidade do portfolio
	# Guarda os valores calculados nas listas vazias:
	port_retornos.append(retornos)
	port_vol.append(vol)
	acoes_pesos.append(pesos)

# O comando abaixo calcula o indice de sharpe de cada portfolio
port_sharpe = (np.array(port_retornos))/np.array(port_vol)
# Printa as Informacoes do melhor portfolio
print('Numero do melhor portfolio: {}'.format(port_sharpe.argmax()))
print('Sharpe do melhor portfolio: {}'.format(port_sharpe.max()))

# O comando abaixo Cria um dicionario para os retornos e os riscos de cada portfolio

portfolio = {'Retornos': port_retornos,
             'Volatilidade': port_vol,
             'Sharpe': port_sharpe}

# O comando abaixo atribui para cada acao o seu respectivo peso no portfolio
for count, ticker in enumerate(tickers):
	portfolio[ticker] = [Pesos[count] for Pesos in acoes_pesos]

    # Cria um dataframe com o dicionario criado acima
df = pd.DataFrame(portfolio)
    # Organiza o dataframe
order = ['Retornos', 'Volatilidade'] + [stock for stock in tickers]
df = df[order]
print('Composicao do melhor portfolio:')
print(df.iloc[port_sharpe.argmax()])

# Cria o gráfico de fronteira eficiente
df.plot.scatter(x='Volatilidade', y='Retornos', c = port_sharpe, cmap = 'viridis', figsize=(10, 8), grid=True)
# Define o rotulo do eixo x
plt.xlabel('Volatilidade (Dsv. Padrao)')
# Define o rotulo do eixo y
plt.ylabel('Retornos Esperados')
# Define um titulo para o grafico
plt.title('Fronteira eficiente')
# y = o retorno do melhor portfolio; x = a volatilidade do melhor portfolio
y = port_retornos[port_sharpe.argmax()]
x = port_vol[port_sharpe.argmax()]
# Plota o ponto correspondente ao melhor portfolio
plt.scatter(x=x,y=y,c='red', s=50)
# Mostra os graficos
plt.show()