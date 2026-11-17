"""Pembanding klasik: nearest neighbor, 2-opt, dan Held-Karp (solusi optimal)."""
import numpy as np


def panjang_rute(d, rute):
    r = np.asarray(rute)
    return float(d[r, np.roll(r, -1)].sum())


def nearest_neighbor(d, awal=0):
    n = len(d)
    rute, belum = [awal], set(range(n)) - {awal}
    while belum:
        terdekat = min(belum, key=lambda j: d[rute[-1], j])
        rute.append(terdekat)
        belum.remove(terdekat)
    return rute


def nn_terbaik(d):
    """Jalankan NN dari setiap kota awal. Kembalikan rute terbaik dan semua panjang."""
    semua = [nearest_neighbor(d, i) for i in range(len(d))]
    panjang = [panjang_rute(d, r) for r in semua]
    return semua[int(np.argmin(panjang))], panjang


def dua_opt(d, rute):
    """2-opt: balik segmen selama ada perbaikan."""
    rute = list(rute)
    n = len(rute)
    membaik = True
    while membaik:
        membaik = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = rute[i], rute[i + 1]
                c, e = rute[j], rute[(j + 1) % n]
                if d[a, c] + d[b, e] < d[a, b] + d[c, e] - 1e-9:
                    rute[i + 1:j + 1] = rute[i + 1:j + 1][::-1]
                    membaik = True
    return rute


def held_karp(d):
    """Solusi optimal dengan DP. Praktis sampai sekitar 15 kota."""
    n = len(d)
    penuh = 1 << (n - 1)
    inf = float("inf")
    dp = np.full((penuh, n - 1), inf)
    induk = np.full((penuh, n - 1), -1, dtype=int)
    for j in range(n - 1):
        dp[1 << j, j] = d[n - 1, j]
    for mask in range(penuh):
        for j in range(n - 1):
            if not mask & (1 << j) or dp[mask, j] == inf:
                continue
            for k in range(n - 1):
                if mask & (1 << k):
                    continue
                m2 = mask | (1 << k)
                nilai = dp[mask, j] + d[j, k]
                if nilai < dp[m2, k]:
                    dp[m2, k] = nilai
                    induk[m2, k] = j
    mask = penuh - 1
    akhir = min(range(n - 1), key=lambda j: dp[mask, j] + d[j, n - 1])
    total = dp[mask, akhir] + d[akhir, n - 1]
    rute, j = [n - 1], akhir
    while j != -1:
        rute.append(j)
        mask, j = mask ^ (1 << j), induk[mask, j]
    return rute, float(total)
