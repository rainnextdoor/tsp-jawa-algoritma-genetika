# Algoritma Genetika untuk Rute Distribusi Logistik Antarkota di Pulau Jawa

Proyek akhir mata kuliah Praktik Kecerdasan Buatan (VTA60237), Teknik Elektronika D4, Universitas Negeri Yogyakarta.

Kode ini mencari rute terpendek yang melewati 30 kota di Pulau Jawa dan kembali ke kota awal. Jarak dihitung dengan rumus Haversine. Masalahnya adalah Traveling Salesman Problem (TSP). Algoritma genetika (GA) dibandingkan dengan nearest neighbor (NN) dan 2-opt.

## Batasan yang perlu dibaca dulu

- Jarak Haversine adalah **garis lurus di permukaan bumi**, bukan jarak jalan. Hasilnya adalah rute terpendek menurut garis lurus, bukan rute tercepat.
- Ini TSP murni. Tidak ada kapasitas kendaraan, jendela waktu, atau banyak kendaraan.
- Koordinat adalah titik pusat wilayah dari data sumber. Titik itu bisa bergeser beberapa kilometer dari pusat kota.
- Jakarta dijadikan satu titik. Lima kota administrasi Jakarta digabung.

## Hasil utama

Semua angka di bawah dihasilkan oleh `python run_all.py` dan tersimpan di folder `results/`. Paper harus memakai angka yang sama.

Panjang rute dalam km. GA dijalankan 30 kali dengan seed 0 sampai 29.

| Metode | Terbaik | Rata-rata | Terburuk | Simpangan baku |
|---|---:|---:|---:|---:|
| Nearest Neighbor (terbaik dari 30 titik awal) | 1932,1 | 1932,1 | 1932,1 | 0 |
| Nearest Neighbor (rata-rata 30 titik awal) | 1932,1 | 2069,8 | 2232,5 | 78,5 |
| NN + 2-opt | 1799,0 | 1799,0 | 1799,0 | 0 |
| **GA (OX + swap)** | **1794,7** | 1817,5 | 1858,8 | 18,5 |
| GA (PMX + swap) | 1828,7 | 2123,9 | 3096,8 | 403,2 |

Cara membaca:

- GA-OX terbaik (1794,7 km) lebih pendek 0,2% dari NN + 2-opt (1799,0 km) dan 7,1% dari NN terbaik.
- Rata-rata GA-OX (1817,5 km) **lebih panjang** dari NN + 2-opt. Satu run 2-opt dari titik NN sudah cukup baik. GA tidak unggul di setiap run.
- PMX jauh lebih buruk dan tidak stabil. OX menjaga urutan relatif kota, dan itu lebih cocok untuk TSP.
- Rute terbaik tidak dibuktikan optimal. Solusi optimal hanya bisa dihitung untuk subset kecil.

Verifikasi optimal (Held-Karp, 12 kota): panjang optimal 1581,83 km. GA menemukan nilai itu pada 10 dari 10 run.

Sweep laju mutasi (GA-OX, 10 run per nilai, seed 0 sampai 9):

| Laju mutasi | Terbaik | Rata-rata | Simpangan baku |
|---:|---:|---:|---:|
| 0,1 | 1803,1 | 1843,7 | 20,6 |
| 0,3 | 1799,2 | 1852,1 | 53,1 |
| 0,5 | 1794,7 | 1810,5 | 17,1 |
| 0,8 | 1805,9 | 1827,4 | 15,7 |

Catatan kejujuran: nilai default laju mutasi 0,5 dipilih setelah uji awal pada seed 0 sampai 2. Sweep memakai seed yang overlap dengan run utama. Perbandingan ini bukan evaluasi pada data terpisah.

Gambar: `results/figures/konvergensi.png` dan `results/figures/rute_terbaik.png`. Urutan kota rute terbaik ada di `results/rute_terbaik_ga.csv`.

## Instalasi

Butuh Python 3.10 atau lebih baru. Uji dilakukan pada Python 3.13.

```bash
git clone https://github.com/rainnextdoor/tsp-jawa-algoritma-genetika.git
cd tsp-jawa-algoritma-genetika
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Cara menjalankan

```bash
python -m pytest -q tests      # 6 tes, sekitar 1 detik
python run_all.py --cepat      # uji cepat, sekitar 30 detik, hasil BUKAN untuk paper
python run_all.py              # eksperimen penuh, sekitar 7 menit pada 2 inti CPU
```

Opsi `--workers N` mengatur jumlah proses paralel. Hasil tidak berubah karena seed tetap.

**Peringatan:** `python run_all.py --cepat` menimpa isi folder `results/` dengan angka uji cepat. Jalankan `python run_all.py` lagi sebelum menulis paper, atau pulihkan dari git dengan `git checkout results/`.

Run penuh membuat ulang `data/kota_jawa.csv` dan `data/matriks_jarak_km.csv` dari data mentah, lalu menulis:

| File | Isi |
|---|---|
| `results/perbandingan_metode.csv` | Tabel hasil utama |
| `results/sweep_mutasi.csv` | Sweep laju mutasi |
| `results/rute_terbaik_ga.csv` | Urutan kota rute terbaik |
| `results/ringkasan.json` | Parameter, seed, dan verifikasi 12 kota |
| `results/figures/*.png` | Kurva konvergensi dan peta rute |

## Parameter GA

| Parameter | Nilai |
|---|---|
| Ukuran populasi | 200 |
| Generasi | 1000 |
| Seleksi | Turnamen, ukuran 5 |
| Crossover | Order Crossover (OX), laju 0,9 |
| Mutasi | Swap dua kota, laju 0,5 per individu |
| Elitisme | 2 individu terbaik |
| Seed | 0 sampai 29 |

Parameter bisa diubah di `src/tspjawa/ga.py` (kelas `ParameterGA`).

## Struktur folder

```
.
├── README.md
├── requirements.txt
├── run_all.py                 # titik masuk eksperimen
├── data/
│   ├── kabupaten-kota-dengan-koordinat.csv   # data mentah (514 baris)
│   ├── kota_jawa.csv                          # 30 kota hasil saringan
│   └── matriks_jarak_km.csv                   # matriks Haversine 30 x 30
├── src/tspjawa/
│   ├── data.py                # saring kota, hitung Haversine
│   ├── baselines.py           # NN, 2-opt, Held-Karp
│   ├── ga.py                  # algoritma genetika
│   └── eksperimen.py          # seluruh eksperimen
├── tests/test_tspjawa.py
├── results/                   # keluaran eksperimen
└── docs/TUTORIAL_GITHUB.md    # cara mengunggah ke GitHub
```

## Dataset

Sumber data mentah: [junwatu/geocode-wilayah-indonesia](https://github.com/junwatu/geocode-wilayah-indonesia), berkas `kabupaten-kota-dengan-koordinat.csv`. Berkas ini kecil (sekitar 30 KB), jadi disertakan di repositori.

Penyaringan: `province_id` 31 sampai 36 (DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, Jawa Timur, Banten), nama diawali "Kota", lalu empat kota administrasi Jakarta dibuang. Hasilnya 30 kota.

**Lisensi data:** repositori sumber tidak mencantumkan lisensi pada halaman yang kami periksa. Sebelum mengumpulkan, cek ulang repositori itu dan tulis status lisensinya di paper.

**Dataset Kaggle:** tugas mewajibkan dataset Kaggle. Berkas ini bukan dari Kaggle. Konfirmasi ke dosen, atau cocokkan koordinat dengan dataset World Cities di Kaggle (juanmah, bersumber dari Simplemaps) dan laporkan selisihnya. Tautan Kaggle itu belum diperiksa di sini, jadi verifikasi sendiri sebelum dikutip.

## Reprodusibilitas

- Semua proses acak memakai `numpy.random.default_rng(seed)`.
- Seed run utama: 0 sampai 29. Seed sweep: 0 sampai 9. Seed verifikasi 12 kota: 0 sampai 9.
- Angka pada tabel di atas berasal dari satu run penuh pada Python 3.13.18, numpy 2.5.3, pandas 3.0.5.
- Versi library lain bisa memberi selisih kecil pada digit desimal.

## Lisensi

Kode: MIT (lihat `LICENSE`). Data mentah mengikuti ketentuan sumber aslinya.

## Anggota kelompok

Isi nama dan NIM anggota di sini sebelum dikumpulkan.
