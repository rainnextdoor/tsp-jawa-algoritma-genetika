import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tspjawa import baselines, data, ga


def test_haversine_jakarta_surabaya():
    kota, d = data.muat()
    i = kota.index[kota["kota"] == "Jakarta"][0]
    j = kota.index[kota["kota"] == "Surabaya"][0]
    assert 650 < d[i, j] < 700  # sekitar 665 km garis lurus


def test_matriks_simetris_dan_diagonal_nol():
    _, d = data.muat()
    assert np.allclose(d, d.T)
    assert np.allclose(np.diag(d), 0)


def test_jumlah_kota():
    kota, _ = data.muat()
    assert len(kota) == 30 and kota["kota"].is_unique


def test_crossover_menghasilkan_permutasi_valid():
    rng = np.random.default_rng(0)
    for f in (ga.order_crossover, ga.pmx_crossover):
        for _ in range(200):
            a, b = rng.permutation(30), rng.permutation(30)
            assert sorted(f(a, b, rng).tolist()) == list(range(30))


def test_ga_reprodusibel_dengan_seed_sama():
    _, d = data.muat()
    p = ga.ParameterGA(generasi=30)
    assert ga.jalankan_ga(d, p, seed=7)[1] == ga.jalankan_ga(d, p, seed=7)[1]


def test_held_karp_sama_dengan_brute_force():
    import itertools
    rng = np.random.default_rng(1)
    xy = rng.random((7, 2))
    d = np.linalg.norm(xy[:, None] - xy[None], axis=2)
    brute = min(baselines.panjang_rute(d, (0,) + p) for p in itertools.permutations(range(1, 7)))
    assert abs(baselines.held_karp(d)[1] - brute) < 1e-9
