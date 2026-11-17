"""Memuat 30 kota di Pulau Jawa dan menghitung matriks jarak haversine."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data" / "kabupaten-kota-dengan-koordinat.csv"
KOTA_CSV = ROOT / "data" / "kota_jawa.csv"
MATRIKS_CSV = ROOT / "data" / "matriks_jarak_km.csv"

PROVINSI = {31: "DKI Jakarta", 32: "Jawa Barat", 33: "Jawa Tengah",
            34: "DI Yogyakarta", 35: "Jawa Timur", 36: "Banten"}
JAKARTA_DIBUANG = ["Kota Jakarta Utara", "Kota Jakarta Barat",
                   "Kota Jakarta Selatan", "Kota Jakarta Timur"]
R_BUMI_KM = 6371.0


def haversine_matrix(lat, lon, r=R_BUMI_KM):
    """Matriks jarak great-circle (km) antar semua pasangan titik."""
    lat, lon = np.radians(lat), np.radians(lon)
    dphi = lat[:, None] - lat[None, :]
    dlmb = lon[:, None] - lon[None, :]
    a = (np.sin(dphi / 2) ** 2
         + np.cos(lat)[:, None] * np.cos(lat)[None, :] * np.sin(dlmb / 2) ** 2)
    return 2 * r * np.arcsin(np.sqrt(a))


def saring_kota(path=RAW_CSV):
    """Ambil kota (bukan kabupaten) di provinsi 31-36. Jakarta jadi satu titik."""
    df = pd.read_csv(path, dtype={"id": str})
    k = df[df["province_id"].between(31, 36) & df["name"].str.startswith("Kota ")]
    k = k[~k["name"].isin(JAKARTA_DIBUANG)].copy()
    k["kota"] = k["name"].str.replace("Kota ", "", regex=False)
    k.loc[k["kota"] == "Jakarta Pusat", "kota"] = "Jakarta"
    k["provinsi"] = k["province_id"].map(PROVINSI)
    k = k.rename(columns={"latitude": "lat", "longitude": "lon"})
    return k[["id", "kota", "provinsi", "lat", "lon"]].reset_index(drop=True)


def siapkan_data():
    """Tulis kota_jawa.csv dan matriks_jarak_km.csv dari CSV mentah."""
    kota = saring_kota()
    assert len(kota) == 30, f"Diharapkan 30 kota, dapat {len(kota)}"
    assert kota[["lat", "lon"]].notna().all().all(), "Ada koordinat kosong"
    kota.to_csv(KOTA_CSV, index=False)
    d = haversine_matrix(kota["lat"].to_numpy(), kota["lon"].to_numpy())
    pd.DataFrame(d.round(2), index=kota["kota"], columns=kota["kota"]).to_csv(MATRIKS_CSV)
    return kota, d


def muat():
    """Kembalikan (DataFrame kota, matriks jarak numpy dalam km)."""
    kota = pd.read_csv(KOTA_CSV)
    d = haversine_matrix(kota["lat"].to_numpy(), kota["lon"].to_numpy())
    return kota, d
