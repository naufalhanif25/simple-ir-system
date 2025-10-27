# Simple IR System CLI

Sistem Information Retrieval (IR) yang dibangun menggunakan bahasa pemrograman **Python** dengan antarmuka Command-Line (CLI). Aplikasi ini mengimplementasikan representasi **Bag of Words (BoW)** dengan **Cosine Similarity** untuk peringkat dokumen dan mengintegrasikan **Whoosh** untuk pengindeksan teks dan kemampuan pencarian yang efisien. Sistem ini mendukung multiple dataset dan memiliki fitur preprocessing teks bahasa Indonesia yang advanced. Konfigurasi dikelola melalui file JSON untuk kustomisasi yang fleksibel.

## Fitur

- **Multi-Dataset Support** - Memproses dokumen dari berbagai sumber termasuk tesis akademik (ETD), artikel berita, dan konten populer
- **Advanced Text Preprocessing** - Pemrosesan bahasa Indonesia khusus dengan case folding, stopword removal, dan stemming menggunakan Sastrawi
- **Hybrid Search Algorithm** - Menggabungkan pengindeksan Whoosh untuk retrievel cepat dengan Cosine Similarity untuk peringkat relevansi
- **Configurable Search Parameters** - Hasil top-K yang dapat disesuaikan, threshold similarity, dan batas pemotongan teks melalui konfigurasi JSON
- **Real-time Search Visualization** - Output CLI berwarna dengan skor similarity dan metadata dokumen
- **Efficient Data Persistence** - Serialisasi Joblib untuk data BoW dan pengindeksan berbasis direktori Whoosh
- **Modular Architecture** - Pemisahan concern dengan kelas TextPreprocessor, DocumentProcessor, dan SearchEngine
- **Cross-Dataset Querying** - Pencarian terpadu di semua dataset yang dimuat dengan atribusi sumber

## Menu CLI

Sistem menyediakan antarmuka CLI interaktif dengan tiga menu utama:

1. **Load Indexed Data** - Memuat data yang sudah diproses sebelumnya (BoW representation dan Whoosh index) untuk menghindari preprocessing ulang
2. **Search Query** - Menerima input query dari pengguna dan menampilkan hasil pencarian dengan ranking similarity
3. **Exit** - Keluar dari aplikasi

## Requirements

Pastikan yang berikut terinstal di sistem Anda:
- Python 3.10 atau lebih baru
- Poetry (opsional, untuk manajemen dependensi)

## Installation & Run

1. **Install dependencies**
    Install dependencies menggunakan Poetry
    ```shell
    poetry install
    ```
    atau install dependencies menggunakan pip
    ```shell
    pip install pandas scikit-learn whoosh sastrawi joblib colorama
    ```

2. **Jalankan program**
    Jalankan program menggunakan `./run.sh`
    ```shell
    chmod +x run.sh
    ./run.sh start
    ```
    atau jalankan program menggunakan **Poetry**
    ```shell
    poetry run python main.py
    ```
    atau jalankan program menggunakan **Python** jika tidak menggunakan **Poetry**
    ```shell
    python main.py
    ```

## Cara Penggunaan

1. **Load Indexed Data** - Pilih opsi 1 untuk memuat data yang sudah diproses
2. **Search Query** - Pilih opsi 2 dan masukkan query pencarian
3. **Exit** - Pilih opsi 3 untuk keluar dari aplikasi

## Dataset

Sistem mendukung berbagai dataset dalam format CSV dengan kolom 'judul' dan 'konten'. Letakkan file dataset Anda dalam folder `datasets/`.