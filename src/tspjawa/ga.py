"""Algoritma genetika untuk TSP: permutasi, turnamen, OX atau PMX, mutasi swap, elitisme."""
from dataclasses import dataclass

import numpy as np


@dataclass
class ParameterGA:
    ukuran_populasi: int = 200
    generasi: int = 1000
    ukuran_turnamen: int = 5
    laju_crossover: float = 0.9
    laju_mutasi: float = 0.5
    elit: int = 2
    crossover: str = "ox"  # "ox" atau "pmx"


def order_crossover(p1, p2, rng):
    n = len(p1)
    a, b = sorted(rng.choice(n, 2, replace=False))
    anak = np.full(n, -1)
    anak[a:b + 1] = p1[a:b + 1]
    dipakai = set(anak[a:b + 1].tolist())
    sisa = [g for g in np.roll(p2, -(b + 1)) if g not in dipakai]
    posisi = [(b + 1 + i) % n for i in range(n - (b - a + 1))]
    for pos, g in zip(posisi, sisa):
        anak[pos] = g
    return anak


def pmx_crossover(p1, p2, rng):
    n = len(p1)
    a, b = sorted(rng.choice(n, 2, replace=False))
    anak = p2.copy()
    anak[a:b + 1] = p1[a:b + 1]
    segmen = set(p1[a:b + 1].tolist())
    for i in list(range(0, a)) + list(range(b + 1, n)):
        g = p2[i]
        while g in segmen:
            g = p2[np.where(p1 == g)[0][0]]
        anak[i] = g
    return anak


def mutasi_swap(rute, rng):
    r = rute.copy()
    i, j = rng.choice(len(r), 2, replace=False)
    r[i], r[j] = r[j], r[i]
    return r


def jalankan_ga(d, param=None, seed=0):
    """Kembalikan (rute terbaik, panjang terbaik, riwayat terbaik per generasi)."""
    param = param or ParameterGA()
    rng = np.random.default_rng(seed)
    n = len(d)
    silang = order_crossover if param.crossover == "ox" else pmx_crossover

    def panjang(pop):
        return d[pop, np.roll(pop, -1, axis=1)].sum(axis=1)

    pop = np.array([rng.permutation(n) for _ in range(param.ukuran_populasi)])
    fit = panjang(pop)
    riwayat = []
    for _ in range(param.generasi):
        urut = np.argsort(fit)
        pop, fit = pop[urut], fit[urut]
        riwayat.append(float(fit[0]))
        baru = [pop[i].copy() for i in range(param.elit)]
        while len(baru) < param.ukuran_populasi:
            ortu = []
            for _ in range(2):
                ikut = rng.choice(len(pop), param.ukuran_turnamen, replace=False)
                ortu.append(pop[ikut[np.argmin(fit[ikut])]])
            if rng.random() < param.laju_crossover:
                anak = silang(ortu[0], ortu[1], rng)
            else:
                anak = ortu[0].copy()
            if rng.random() < param.laju_mutasi:
                anak = mutasi_swap(anak, rng)
            baru.append(anak)
        pop = np.array(baru)
        fit = panjang(pop)
    k = int(np.argmin(fit))
    riwayat.append(float(fit[k]))
    return pop[k].tolist(), float(fit[k]), riwayat
