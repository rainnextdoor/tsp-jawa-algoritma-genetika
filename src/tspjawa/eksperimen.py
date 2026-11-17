"""Menjalankan seluruh eksperimen paper. Hasil ditulis ke folder results/."""
import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import baselines, data, ga

HASIL = data.ROOT / "results"
SEED_AWAL = 0
# 12 kota untuk verifikasi optimal dengan Held-Karp (brute force 11!/2 = 19,9 juta rute).
KOTA_UJI = ["Jakarta", "Bogor", "Bandung", "Cirebon", "Semarang", "Yogyakarta",
            "Surakarta", "Madiun", "Malang", "Surabaya", "Serang", "Tegal"]


def _satu_run(args):
    d, param, seed = args
    _, panjang, riwayat = ga.jalankan_ga(d, param, seed)
    return seed, panjang, riwayat


def _banyak_run(d, param, jumlah_seed, pekerja):
    tugas = [(d, param, SEED_AWAL + s) for s in range(jumlah_seed)]
    with ProcessPoolExecutor(max_workers=pekerja) as ex:
        return sorted(ex.map(_satu_run, tugas))


def ringkas(nilai):
    v = np.asarray(nilai)
    return {"terbaik": v.min(), "rata2": v.mean(), "terburuk": v.max(), "simpangan_baku": v.std(ddof=1) if len(v) > 1 else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30, help="jumlah run independen per konfigurasi")
    ap.add_argument("--seeds-sweep", type=int, default=10, help="jumlah run per titik sweep mutasi")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--cepat", action="store_true", help="mode uji cepat (hasil tidak untuk paper)")
    a = ap.parse_args()
    if a.cepat:
        a.seeds, a.seeds_sweep = 3, 2
    HASIL.mkdir(exist_ok=True)
    (HASIL / "figures").mkdir(exist_ok=True)
    t0 = time.time()

    data.siapkan_data()
    kota, d = data.muat()
    param = ga.ParameterGA(generasi=200) if a.cepat else ga.ParameterGA()

    # 1. Baseline deterministik
    rute_nn, semua_nn = baselines.nn_terbaik(d)
    rute_2opt = baselines.dua_opt(d, rute_nn)
    len_nn, len_2opt = min(semua_nn), baselines.panjang_rute(d, rute_2opt)

    # 2. GA: OX dan PMX
    hasil = {}
    for nama in ("ox", "pmx"):
        p = ga.ParameterGA(**{**asdict(param), "crossover": nama})
        runs = _banyak_run(d, p, a.seeds, a.workers)
        hasil[nama] = runs
        print(f"GA-{nama.upper()} selesai ({time.time() - t0:.0f} dtk)", flush=True)

    # 3. Sweep laju mutasi (OX)
    sweep = {}
    for m in (0.1, 0.3, 0.5, 0.8):
        p = ga.ParameterGA(**{**asdict(param), "laju_mutasi": m})
        sweep[m] = [r[1] for r in _banyak_run(d, p, a.seeds_sweep, a.workers)]
        print(f"sweep mutasi {m} selesai", flush=True)

    # 4. Verifikasi dengan Held-Karp pada 12 kota
    idx = [int(np.where(kota["kota"] == k)[0][0]) for k in KOTA_UJI]
    d12 = d[np.ix_(idx, idx)]
    _, optimal12 = baselines.held_karp(d12)
    ga12 = [ga.jalankan_ga(d12, ga.ParameterGA(generasi=200), seed=s)[1] for s in range(10)]

    # Tabel utama
    baris = [
        {"metode": "Nearest Neighbor (terbaik dari 30 awal)", **ringkas([len_nn])},
        {"metode": "Nearest Neighbor (rata-rata 30 awal)", **ringkas(semua_nn)},
        {"metode": "NN + 2-opt", **ringkas([len_2opt])},
        {"metode": "GA (OX + swap)", **ringkas([r[1] for r in hasil["ox"]])},
        {"metode": "GA (PMX + swap)", **ringkas([r[1] for r in hasil["pmx"]])},
    ]
    tabel = pd.DataFrame(baris)
    tabel.round(2).to_csv(HASIL / "perbandingan_metode.csv", index=False)
    pd.DataFrame([{"laju_mutasi": m, **ringkas(v)} for m, v in sweep.items()]).round(2).to_csv(
        HASIL / "sweep_mutasi.csv", index=False)

    # Rute terbaik GA-OX
    terbaik_seed = min(hasil["ox"], key=lambda r: r[1])[0]
    rute_ga, len_ga, _ = ga.jalankan_ga(d, ga.ParameterGA(**{**asdict(param), "crossover": "ox"}), terbaik_seed)
    pd.DataFrame({"urutan": range(1, 31), "kota": kota["kota"].to_numpy()[rute_ga]}).to_csv(
        HASIL / "rute_terbaik_ga.csv", index=False)

    ringkasan = {
        "parameter_ga": asdict(param), "seed_awal": SEED_AWAL, "jumlah_run": a.seeds,
        "panjang_rute_ga_terbaik_km": round(len_ga, 2), "seed_terbaik": terbaik_seed,
        "panjang_nn_terbaik_km": round(len_nn, 2), "panjang_2opt_km": round(len_2opt, 2),
        "verifikasi_12_kota": {"optimal_held_karp_km": round(optimal12, 2),
                               "ga_terbaik_km": round(min(ga12), 2),
                               "ga_menemukan_optimal_dari_10_run": int(sum(abs(x - optimal12) < 1e-6 for x in ga12))},
        "waktu_total_detik": round(time.time() - t0),
    }
    (HASIL / "ringkasan.json").write_text(json.dumps(ringkasan, indent=2, ensure_ascii=False))

    # Gambar
    riw = np.array([r[2] for r in hasil["ox"]])
    plt.figure(figsize=(6, 3.6))
    plt.plot(riw.mean(axis=0), label="GA-OX (rata-rata)")
    plt.fill_between(range(riw.shape[1]), riw.min(axis=0), riw.max(axis=0), alpha=0.2, label="min-maks")
    plt.axhline(len_nn, ls="--", c="gray", label="NN terbaik")
    plt.axhline(len_2opt, ls=":", c="k", label="NN + 2-opt")
    plt.xlabel("Generasi"); plt.ylabel("Panjang rute (km)"); plt.legend(); plt.tight_layout()
    plt.savefig(HASIL / "figures" / "konvergensi.png", dpi=200); plt.close()

    plt.figure(figsize=(6, 4))
    lat, lon = kota["lat"].to_numpy(), kota["lon"].to_numpy()
    r = np.array(rute_ga + [rute_ga[0]])
    plt.plot(lon[r], lat[r], "-o", ms=4, lw=1)
    for i in range(30):
        plt.annotate(kota["kota"][i], (lon[i], lat[i]), fontsize=6, xytext=(2, 2), textcoords="offset points")
    plt.xlabel("Bujur"); plt.ylabel("Lintang"); plt.title(f"Rute terbaik GA: {len_ga:.1f} km")
    plt.tight_layout(); plt.savefig(HASIL / "figures" / "rute_terbaik.png", dpi=200); plt.close()

    print(tabel.round(1).to_string(index=False))
    print(json.dumps(ringkasan["verifikasi_12_kota"]))


if __name__ == "__main__":
    main()
