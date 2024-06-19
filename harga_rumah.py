import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import tkinter as tk
from tkinter import ttk, messagebox
import locale
import os
import sys

# Set locale untuk format angka Indonesia
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

# Mendapatkan path direktori saat menjalankan skrip
def resource_path(relative_path):
    """ Dapatkan path absolut ke resource, bekerja untuk development dan PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Path ke file excel
file_path = resource_path('HARGA_RUMAH_JAKSEL.xlsx')
df = pd.read_excel(file_path, sheet_name='Sheet1', skiprows=1)
df.columns = ['HARGA', 'LT', 'LB', 'JKT', 'JKM', 'GRS', 'KOTA']
df = df.dropna()  # Menghapus baris yang memiliki nilai kosong

# Mengubah kolom 'GRS' (ketersediaan garasi) menjadi nilai numerik
df['GRS'] = df['GRS'].map({'ADA': 1, 'TIDAK': 0})

# Mengonversi semua kolom yang relevan menjadi tipe numerik
df[['HARGA', 'LT', 'LB', 'JKT', 'JKM', 'GRS']] = df[['HARGA', 'LT', 'LB', 'JKT', 'JKM', 'GRS']].apply(pd.to_numeric, errors='coerce')

# Menghapus baris yang masih memiliki nilai kosong setelah konversi
df = df.dropna()

# Memilih fitur dan variabel target
X = df[['LT', 'LB', 'JKT', 'JKM', 'GRS']]
y = df['HARGA']

# Normalisasi fitur
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Membagi data menjadi set pelatihan dan set pengujian
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Melatih model regresi linear
model = LinearRegression()
model.fit(X_train, y_train)

# Fungsi untuk memprediksi harga rumah
def predict_price(lt, lb, jkt, jkm, grs):
    grs_encoded = 1 if grs.lower() == 'y' else 0  # Mengubah input 'y'/'t' menjadi 1/0
    input_data = scaler.transform([[lt, lb, jkt, jkm, grs_encoded]])  # Skalakan input
    predicted_price = model.predict(input_data)[0]
    return predicted_price

# Menghitung MAPE secara manual
y_pred = model.predict(X_test)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")

def clear_inputs():
    entry_lt.delete(0, tk.END)
    entry_lb.delete(0, tk.END)
    entry_jkt.delete(0, tk.END)
    entry_jkm.delete(0, tk.END)
    entry_grs.delete(0, tk.END)
    label_result.config(text="")

# Fungsi untuk menghitung dan menampilkan prediksi harga dan MAPE
def on_predict():
    try:
        lt = float(entry_lt.get())
        lb = float(entry_lb.get())
        jkt = int(entry_jkt.get())
        jkm = int(entry_jkm.get())
        grs = entry_grs.get()
        predicted_price = predict_price(lt, lb, jkt, jkm, grs)
        formatted_price = locale.format_string("%d", predicted_price, grouping=True)
        result_var.set(f"Prediksi Harga: Rp {formatted_price},00")
        mape_var.set(f"MAPE: {mape:.2f}%")
    except ValueError:
        messagebox.showerror("Input Error", "Mohon masukkan nilai yang valid")

# Membuat antarmuka pengguna dengan Tkinter
root = tk.Tk()
root.title("Prediksi Harga Rumah")

# Menambahkan label dan entry untuk setiap input
ttk.Label(root, text="Luas Tanah (LT)").grid(row=0, column=0, padx=10, pady=5)
entry_lt = ttk.Entry(root)
entry_lt.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(root, text="Luas Bangunan (LB)").grid(row=1, column=0, padx=10, pady=5)
entry_lb = ttk.Entry(root)
entry_lb.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(root, text="Jumlah Kamar Tidur (JKT)").grid(row=2, column=0, padx=10, pady=5)
entry_jkt = ttk.Entry(root)
entry_jkt.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(root, text="Jumlah Kamar Mandi (JKM)").grid(row=3, column=0, padx=10, pady=5)
entry_jkm = ttk.Entry(root)
entry_jkm.grid(row=3, column=1, padx=10, pady=5)

ttk.Label(root, text="Garasi (y/t)").grid(row=4, column=0, padx=10, pady=5)
entry_grs = ttk.Entry(root)
entry_grs.grid(row=4, column=1, padx=10, pady=5)

# Menambahkan tombol untuk memprediksi harga
predict_button = ttk.Button(root, text="Prediksi Harga", command=on_predict)
predict_button.grid(row=5, column=0, columnspan=2, pady=10)

# Menambahkan label untuk menampilkan hasil prediksi dan MAPE
result_var = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_var)
result_label.grid(row=6, column=0, columnspan=2, pady=5)

button_clear = tk.Button(root, text="Clear", command=clear_inputs)
button_clear.grid(row=5, column=1, columnspan=2)

mape_var = tk.StringVar()
mape_label = ttk.Label(root, textvariable=mape_var)
mape_label.grid(row=7, column=0, columnspan=2, pady=5)

label_result = tk.Label(root, text="", font=("Arial", 12))
label_result.grid(row=7, column=0, columnspan=2)

# Menjalankan aplikasi
root.mainloop()
