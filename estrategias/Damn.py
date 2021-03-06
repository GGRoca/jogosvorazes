import importlib
from estrategias.jogadores import Jogador
from collections import defaultdict
import numpy as np
import pandas as pd
nameschars = ["Fuck", "Damn", "Shit"]
namechar = nameschars[1]
alt = len(nameschars) - 1
porc = 0.6
medi = lambda x: (np.sqrt(400) - np.sqrt(x))/100

class MeuJogador(Jogador):
    def aprox(self, n):
        saida = [(a,abs(self.historico[a]['reputacao']-n)) for a in self.jogadores]
        a = min(saida, key=lambda x: x[1])[0]
        self.jogadores.remove(a)
        return a

    def __init__(self):
        self.historico = defaultdict(lambda: {"comida": 0, "reputacao": 0, "cacou": 0, "descansou": 0, "var":0})
        self.self = {"cacou": 0, "descansou": 0, "ult":0}
        self.jogadores = None 
        
    def escolha_de_cacada(self, rodada, comida_atual, reputacao_atual, m, reputacoes_dos_jogadores):
        if rodada > 1:
            if isinstance(reputacao_atual, np.ndarray):
                reputacao_atual = reputacao_atual[0]
            escolhas = [None]*len(reputacoes_dos_jogadores)
            
            o = sum([self.historico[i]["reputacao"] for i in nameschars[1:]])
            c, d, t, u = self.self['cacou'], self.self['descansou'], len(reputacoes_dos_jogadores) - alt, self.self['ult']
            m = (sum(reputacoes_dos_jogadores)-o)/t + medi(rodada) if t > 0 else 0
            b = (1-m)*t - (d+c)*m + c - u*t
            b = b//1 + 1 if b > 0 else 1
            
            maxcomida, var = sorted([self.historico[i]["comida"] for i in self.jogadores], reverse=True)[:int(b+alt)], 0
            
            for k,i in enumerate(reputacoes_dos_jogadores):
                j = None
                if isinstance(i, np.ndarray):
                    i, j = i[0], i
                quem = self.aprox(i)
                
                if quem in nameschars:
                    escolhas[k] = 'c'
                elif self.historico[quem]["comida"] in maxcomida:
                    escolhas[k] = 'd'
                    var -= 1
                else:
                    try:
                        lista = [reputacao_atual]+list(reputacoes_dos_jogadores)
                        if j == None: 
                            lista.remove(i)
                        else:
                            lista.remove(j)
                        play = importlib.import_module("estrategias.{}".format(quem)).MeuJogador()
                        escolhas[k] = play.escolha_de_cacada(rodada, self.historico[quem]["comida"] + comida_atual - self.historico[namechar]["comida"], i, m, tuple(lista[:t]))[0]
                    except:
                        if rodada > 2:
                            if self.historico[quem]["var"] > 0:
                                escolhas[k] = 'd'
                            else:
                                escolhas[k] = 'c'
                        else:
                            escolhas[k] = np.random.choice(['d', 'c'], p=(1-porc, porc))
                if escolhas[k] == 'd':
                    var += 1
            self.self['ult'] = var/t if var >= 0 and t > 0 else 0
                            
        else:
            escolhas = list(np.random.choice(['d', 'c'], size=len(reputacoes_dos_jogadores), p=(1-porc, porc)))
            self.self["ult"] = escolhas.count('d')/len(escolhas)
        return escolhas
    
    def resultado_da_cacada(self, comida_ganha):
        escolhas = pd.DataFrame(comida_ganha)
        self.jogadores = list(escolhas.columns)
        if namechar in self.jogadores:
            self.self["cacou"] += sum([e == -3 or e == 0 for e in escolhas[namechar]])
            self.self["descansou"] += sum([e == -2 or e == 1 for e in escolhas[namechar]])
            self.jogadores.remove(namechar)
        for nome in self.jogadores:
            self.historico[nome]["cacou"] += sum([e == -3 or e == 0 for e in escolhas[nome]])
            self.historico[nome]["descansou"] += sum([e == -2 or e == 1 for e in escolhas[nome]])
            self.historico[nome]["comida"] += sum(escolhas[nome])
            var = self.historico[nome]["cacou"] / (float(self.historico[nome]["cacou"] + self.historico[nome]["descansou"]))
            self.historico[nome]["var"] =  self.historico[nome]["reputacao"] - var
            self.historico[nome]["reputacao"] = var