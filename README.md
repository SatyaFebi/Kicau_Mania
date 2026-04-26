# Kicau Mania - Dance Detector 🕺🐱

Project ini adalah aplikasi deteksi pose Scuba/Kicau Mania sederhana menggunakan **MediaPipe** dan **OpenCV**. Saat kamu melakukan pose Scuba/Kicau Mania di depan kamera, aplikasi akan mendeteksi gerakan tersebut dan memicu munculnya video overlay "Scuba Cat" yang menari disertai dengan musik.

## ✨ Fitur
- **Real-time Pose Detection**: Menggunakan MediaPipe untuk mendeteksi titik tubuh.
- **Dynamic Overlay**: Menampilkan video kucing menari di sisi kiri dan kanan layar.
- **Audio Sync**: Musik akan otomatis berputar saat kamu melakukan pose tari dan berhenti saat kamu berhenti.
- **Auto Audio Extraction**: Otomatis mengekstrak audio dari video jika file MP3 belum tersedia.

## 🛠️ Persiapan & Setup

### 1. Prasyarat
Pastikan kamu sudah menginstal **Python 3.8** atau versi yang lebih baru.

### 2. Instalasi Library
Aplikasi ini direkomendasikan menggunakan **[uv](https://github.com/astral-sh/uv)** untuk manajemen package yang super cepat. Jalankan perintah berikut untuk menginstal semua library:

```bash
uv sync
```

### 3. Struktur File
Pastikan file video berada di folder yang benar:
- `assets/video/scuba_cat_dance.mp4`

## 🚀 Cara Menjalankan
Jalankan script utama menggunakan `uv run`:

```bash
uv run dance_detector.py
```

Tunggu hingga jendela webcam muncul. Untuk keluar dari aplikasi, tekan tombol **ESC**.

## 💃 Cara Melakukan Pose (Trigger)
Aplikasi ini akan mendeteksi pose "Tarian Kicau Mania". Berikut cara melakukannya:

1. **Satu tangan menyentuh mulut/wajah**: Angkat tangan kiri atau kanan hingga mendekati area hidung atau mulut.
2. **Tangan lainnya direntangkan**: Rentangkan tangan yang satu lagi menjauh dari tubuh (ke arah samping).

**Contoh:**
- Tangan **Kiri** di mulut + Tangan **Kanan** direntangkan ke samping.
- **ATAU**
- Tangan **Kanan** di mulut + Tangan **Kiri** direntangkan ke samping.

Jika pose terdeteksi, status akan berubah dan video kucing menari akan muncul di layar!

---
Selamat menari! 🎶
