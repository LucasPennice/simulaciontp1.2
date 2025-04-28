import random
import argparse
import matplotlib.pyplot as plt
from functools import reduce


def martingala(cantidad_actual, apuesta_base, perdidas_consecutivas, _1, _2):
    return apuesta_base * (2 ** perdidas_consecutivas)

def d_alembert(cantidad_actual, apuesta_base, perdidas_consecutivas, _1, _2):
    return max(apuesta_base + perdidas_consecutivas * apuesta_base, apuesta_base)

def fibonacci(cantidad_actual, apuesta_base, perdidas_consecutivas, _1, _2):
    fib = [1, 1]
    for _ in range(perdidas_consecutivas - 1):
        fib.append(fib[-1] + fib[-2])
    return apuesta_base * fib[-1] if perdidas_consecutivas else apuesta_base

def estrategia_propia(cantidad_actual, apuesta_base, _, ultima_apuesta, ultima_victoria):
    if ultima_victoria:
        
        nueva_apuesta = min(cantidad_actual, ultima_apuesta * 2)
    else:
        
        nueva_apuesta = min(cantidad_actual, apuesta_base)
    return nueva_apuesta


def girar_ruleta():
    return random.randint(0, 36)

def apostar(color_elegido):
    bola = girar_ruleta()
    if bola == 0:
        return False
    if color_elegido == 'rojo':
        return bola % 2 == 1  
    else:
        return bola % 2 == 0  


def simular(capital_inicial, estrategia, capital_infinito, n_tiradas=500, apuesta_base=10):
    capital = capital_inicial
    historial = [capital]
    perdidas_consecutivas = 0
    banca_rota = False
    ultima_apuesta = apuesta_base
    ultima_victoria = False

    for _ in range(n_tiradas):
        if not capital_infinito and capital <= 0:
            banca_rota = True
            break

        
        apuesta = estrategia(capital, apuesta_base, perdidas_consecutivas, ultima_apuesta, ultima_victoria)

        if not capital_infinito and apuesta > capital:
            apuesta = capital

        resultado = apostar('rojo')

        if resultado:
            capital += apuesta
            perdidas_consecutivas = 0
            ultima_victoria = True
        else:
            capital -= apuesta
            perdidas_consecutivas += 1
            ultima_victoria = False

        
        ultima_apuesta = apuesta

        historial.append(capital)

    return historial, banca_rota

def calcular_rachas_de_derrota(historial):
    rachas = []
    racha_actual = 0

    for i in range(1, len(historial)):
        if historial[i] < historial[i - 1]:  # Si pierdes
            racha_actual += 1
        else:  # Si ganas
            if racha_actual > 0:
                rachas.append(racha_actual)  # Agregar la racha actual a la lista
            racha_actual = 0  # Reiniciar la racha

    # Si la última racha no se reinició (porque el historial terminó con derrotas)
    if racha_actual > 0:
        rachas.append(racha_actual)

    return rachas

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=int, required=True, help='Número de corridas')
    parser.add_argument('-n', type=int, required=True, help='Número de tiradas')
    parser.add_argument('-s', required=True, choices=['m', 'd', 'f', 'o'], help='Estrategia: m (Martingala), d (D’Alembert), f (Fibonacci), o (Otra)')
    parser.add_argument('-a', required=True, choices=['i', 'f'], help='Capital: i (infinito), f (finito)')
    args = parser.parse_args()

    estrategias = {
        'm': martingala,
        'd': d_alembert,
        'f': fibonacci,
        'o': estrategia_propia
    }

    estrategia_seleccionada = estrategias[args.s]
    capital_infinito = args.a == 'i'
    n_corridas = args.c
    n_tiradas = args.n
    CAPITAL_INICIAL = 1000

    corridas = []
    bancarrotas = 0

    frecuencia_relativa_final = []
    
    rachas_de_derrota = []

    for indice_corrida in range(n_corridas):
        historial, banca_rota = simular(
            capital_inicial=CAPITAL_INICIAL,
            estrategia=estrategia_seleccionada,
            capital_infinito=capital_infinito,
            n_tiradas=n_tiradas
        )
        
        rachas_de_derrota.extend(calcular_rachas_de_derrota(historial))
        
        corridas.append(historial)
        
        if banca_rota:
            bancarrotas += 1

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    
    for idx, historial in enumerate(corridas):
        plt.plot(historial, label=f'Corrida {idx+1}')

    plt.axhline(y=CAPITAL_INICIAL, color='b', linestyle='--', label='Capital inicial')

    plt.title('Evolución del Capital')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Capital ($)')
    plt.legend()
    plt.grid()

    diccionario_frecuencias = {}
    
    for idx in rachas_de_derrota:
        if idx in diccionario_frecuencias:
            diccionario_frecuencias[idx] += 1
        else:
            diccionario_frecuencias[idx] = 1

    categorias, frecuencias = zip(*sorted(diccionario_frecuencias.items()))
    categorias = list(categorias)
    frecuencias = list(frecuencias)
    
    for idx, i in enumerate(frecuencias):
        frecuencias[idx] = i / len(rachas_de_derrota)
    
    # Graficar frecuencia relativa de tiradas positivas
    plt.subplot(1, 2, 2)  

    plt.bar(categorias, frecuencias, alpha=1)

    plt.title('Frecuencia Relativa de Tiradas Positivas')
    plt.xlabel('Número de tiradas (n)')
    plt.ylabel('Frecuencia relativa')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()  

if __name__ == '__main__':
    main()