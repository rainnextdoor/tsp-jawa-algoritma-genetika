# Tutorial: Mengunggah Proyek ke GitHub

Tutorial ini untuk pemula. Ikuti urutannya.

## A. Persiapan (sekali saja)

1. Buat akun di https://github.com.
2. Pasang Git dari https://git-scm.com/downloads.
3. Buka terminal (Git Bash di Windows) lalu atur identitas:

```bash
git config --global user.name "Nama Kamu"
git config --global user.email "email-github-kamu@example.com"
```

Pakai email yang sama dengan akun GitHub.

## B. Buat repositori kosong di GitHub

1. Klik tombol **+** di kanan atas, lalu **New repository**.
2. Isi nama, misalnya `tsp-jawa-algoritma-genetika`.
3. Pilih **Public** agar dosen bisa membuka tanpa undangan.
4. **Jangan** centang "Add a README", ".gitignore", atau "license". Proyek ini sudah punya semuanya.
5. Klik **Create repository**. Salin URL repositori (bentuk HTTPS).

## C. Unggah dari komputer

Masuk ke folder proyek, lalu jalankan:

```bash
cd tsp_jawa
git init
git branch -M main
git add .
git status
git commit -m "Versi awal: GA untuk TSP 30 kota di Pulau Jawa"
git remote add origin https://github.com/USERNAME/tsp-jawa-algoritma-genetika.git
git push -u origin main
```

Ganti `USERNAME` dengan nama akunmu.

Saat `git push` meminta login, GitHub tidak menerima kata sandi akun. Pakai **Personal Access Token**:

1. Buka GitHub, **Settings**, **Developer settings**, **Personal access tokens**, **Tokens (classic)**.
2. Klik **Generate new token**, centang izin `repo`, lalu buat.
3. Salin token itu. Tempel sebagai kata sandi saat diminta.

Alternatif tanpa terminal: pasang **GitHub Desktop**, pilih **Add local repository**, lalu **Publish repository**.

## D. Periksa sebelum mengumpulkan

Buka URL repositori di browser. Pastikan:

- README tampil di halaman utama.
- Folder `src/`, `data/`, `results/`, `tests/`, dan `docs/` ada.
- Gambar di `results/figures/` bisa dibuka.
- Tidak ada file `.venv/` atau `__pycache__/` (sudah dicegah oleh `.gitignore`).

Uji dari nol, seperti yang akan dilakukan penilai:

```bash
git clone https://github.com/USERNAME/tsp-jawa-algoritma-genetika.git uji
cd uji
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q tests
python run_all.py --cepat
```

Kalau semua jalan, repositori siap.

## E. Memperbarui setelah ada perubahan

```bash
git add .
git commit -m "Jelaskan perubahan singkat"
git push
```

## F. Menandai versi yang dikumpulkan

Beri tag agar versi untuk penilaian jelas, lalu tulis tag itu di paper.

```bash
git tag -a v1.0 -m "Versi pengumpulan akhir"
git push origin v1.0
```

## G. Masalah yang sering muncul

| Pesan atau gejala | Penyebab | Solusi |
|---|---|---|
| `Authentication failed` | Memakai kata sandi akun | Pakai Personal Access Token |
| `remote origin already exists` | Remote sudah pernah ditambah | `git remote set-url origin URL_BARU` |
| `rejected ... fetch first` | Repositori GitHub punya commit yang belum ada di lokal | `git pull --rebase origin main`, lalu `git push` |
| `file larger than 100 MB` | Ada file data besar | Hapus dari repositori, tautkan di README |
| README tidak tampil rapi | Nama file salah | Pastikan namanya `README.md` |

## H. Catatan dataset

Dataset proyek ini kecil (sekitar 30 KB), jadi ikut diunggah. Kalau ada dataset di atas 50 MB, jangan diunggah. Taruh tautan Kaggle di README dan jelaskan cara mengunduhnya.
