import sympy as sp


def ComputePE(A : str, B : str, p, return_trans_matr=False):
    '''
    Dla wzorców A, B zwraca prawd. wygrania A oraz wart. oczekiwaną czasu gry.
    Gdy p jest symbolem zwraca symboliczne wyrażenie, a gdy liczbą - wynik liczbowy.
    '''
    if len(A) != 3 and len(B) != 3:
        raise ValueError('Wzorce muszą mieć długość 3.')
    A = A.lower()
    B = B.lower()
    stany = ['oo', 'or', 'ro', 'rr', A, B]
    stany_dict = {stan: i for i, stan in enumerate(stany)}
    q = 1-p

    mu = sp.Matrix([[p*p, p*q, p*q, q*q]])

    P = sp.zeros(6,6)
    P[4,4] = P[5,5] = 1
    for i, stan in enumerate(stany[:4]):
        sR = stan + 'r'
        sO = stan + 'o'
        if sR not in [A, B]:
            sR = sR[1:]
        P[i, stany_dict[sR]] = q
        if sO not in [A, B]:
            sO = sO[1:]
        P[i, stany_dict[sO]] = p

    Q = P[:4, :4]
    R = P[:4, 4:]

    u_k = sp.symbols('u1:5')
    u = sp.linsolve((sp.eye(4) - Q, R[:, 0]), u_k)
    u = sp.Matrix(next(iter(u)))

    prawd = mu*u
    prawd = sp.factor(prawd[0])

    t_k = sp.symbols('t1:5')
    t = sp.linsolve((sp.eye(4) - Q, sp.ones(4)), t_k)
    t = sp.Matrix(next(iter(t)))

    wartOczek = mu*t
    wartOczek = sp.factor(wartOczek[0] + 2)

    if return_trans_matr:
        return prawd, wartOczek, P
    return prawd, wartOczek

def ComputeHalf(prawd):
    '''
    Rozwiązuje prawd=1/2, czyli zwraca prawd. dla którego A i B mają jednakowe szanse.
    Może zwrócić coś dziwnego.
    '''
    eq = sp.factor(prawd - sp.S(1)/2)
    half = sp.solveset(eq, domain=sp.Interval.open(0,1))
    return half

def IntToCoins(n : int):
    '''
    Zwraca wzorzec dł. 3, który binarnie jest równy n, gdzie 'o'=0, 'r'=1.
    '''
    if n < 0 or n > 7:
        raise ValueError('Argument spoza zakresu [0,7].')
    coins = ''
    numToCoin = {0: 'o',
                 1: 'r'}
    while n > 0:
        coins = numToCoin[n % 2] + coins
        n = n // 2
    return 'o' * (3 - len(coins)) + coins

def FracToLatex(expr):
    '''
    Dla ułamka sympy.Rational zwraca ułamek mieszany w latex'u.
    '''
    if isinstance(expr, sp.Rational) and expr.q != 1:
        whole = ''
        if expr.p > expr.q: 
            whole = expr.p // expr.q
        part = expr.p % expr.q
        return fr'${whole}\,\sfrac{{{part}}}{{{expr.q}}}$' # \sfrac z paczki xfrac
    return f'${expr}$'