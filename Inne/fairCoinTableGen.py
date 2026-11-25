# Ten skrypt oblicza prawd. oraz wart. oczekiwane dla wszystkich par (A, B)
# dla p=1/2 oraz tworzy tabelkę z tymi wartościami w latexu.
# Latex wymaga paczek booktabs, xfrac.

import pandas as pd
from sympy import S

from metody import ComputePE, FracToLatex, IntToCoins

colNames = ['A', 
            'B', 
            r'$\mathbb P(\tau_A < \tau_B)$', 
            r'$\mathbb E\tau$']
rows = [] # A, B, Prawd, E

for i in range(8):
    A = IntToCoins(i)
    for j in range(i + 1, 8):
        B = IntToCoins(j)
        prawd, wartOczek = ComputePE(A, B, S(1)/2)
        rows.append([A.upper(), 
                     B.upper(), 
                     FracToLatex(prawd), 
                     FracToLatex(wartOczek)])

df = pd.DataFrame(rows, columns=colNames)
latexCode = df.to_latex(index=False, 
                        escape=False, 
                        column_format='cccc') # to_latex oprócz pandas wymaga Jinja2

with open('fairCoinTable.tex', 'w', encoding='utf-8') as f:
    f.write(latexCode)
