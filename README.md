# A. Download dan Setup XAMPP

## 📋 Prasyarat

- Download XAMPP, liat link tutorial ini https://youtu.be/ZCgyo1cgHTg?si=IyHONziLdFznmwAf

---

# B. Import Database

## 1. Menjalankan XAMPP

1. Buka **XAMPP Control Panel** (search aja di windows kalo gada di home)
2. Klik **Start** pada **Apache**
3. Klik **Start** pada **MySQL**
4. Pastikan kedua status berubah menjadi **hijau (Running)**

---

## 2. Masuk ke halaman Database

1. Masih di **XAMPP Control Panel**, klik **Admin** pada **MySQL**
2. Nanti diarahin ke browser

---

## 3. Membuat Database

1. Buka browser
2. Klik **"New"** di sidebar kiri
3. Isi nama database: `mager_db`
4. Klik **"Create"**

---

## 4. Mengimpor Database

1. Klik `mager_db`, database yang baru dibuat di sidebar kiri
2. Pilih tab **"Import"** di bagian atas
3. Klik **"Choose File"** → pilih file `db.sql` yang ada di repo ini (masuk ke folder database, nnti ada db.sql)
4. Scroll ke bawah, klik **"Go"** / **"Import"**
5. Tunggu hingga muncul pesan sukses berwarna hijau

---

# UDAH, TINGGAL JALANIN AJA APP NYA PAKE "py app.py"
