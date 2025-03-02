import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import time

def run_simulation():
    try:
        arrangement = arrangement_entry.get()
        type_ = type_entry.get()
        geometry = geometry_entry.get()
        thickness = thickness_entry.get()
        sensors = sensor_entry.get()

        if not all([arrangement, type_, geometry, thickness, sensors]):
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun!")
            return

        work_dir = "/Users/oykubeysi/Geant4-Plastic-Scintillator-Simulation/build"
        sim_path = os.path.join(work_dir, "sim")
        macro_file = os.path.join(work_dir, "run.mac")
        root_file = os.path.join(work_dir, "R_BC404_20mm_2Sensors.root")  # ROOT dosyası

        command = [sim_path, arrangement, type_, geometry, thickness, sensors, macro_file]

        # Simülasyonu başlat
        process = subprocess.Popen(command, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

        def read_output():
            for line in process.stdout:
                output_text.insert(tk.END, line)
                output_text.see(tk.END)
            process.stdout.close()

        def read_errors():
            for line in process.stderr:
                output_text.insert(tk.END, f"[Hata] {line}")
                output_text.see(tk.END)
            process.stderr.close()

        threading.Thread(target=read_output, daemon=True).start()
        threading.Thread(target=read_errors, daemon=True).start()

        # ROOT dosyasını açma işlemi
        def wait_and_open_root():
            process.wait()  # Simülasyonun tamamlanmasını bekle

            # ROOT dosyasının oluşmasını 10 saniye bekle
            timeout = 10
            while timeout > 0:
                if os.path.exists(root_file):
                    answer = messagebox.askyesno("Tamamlandı", "Simülasyon tamamlandı! ROOT dosyasını açmak ister misiniz?")
                    if answer:
                        # ROOT açıldığında new TBrowser komutunu çalıştır
                        root_command = f'root -l -e "TFile::Open(\\"{root_file}\\"); new TBrowser;"'
                        root_process = subprocess.Popen(root_command, shell=True)

                        # ROOT kapanmasını bekle ve ardından Geant4'ü sonlandır
                        root_process.wait()
                        messagebox.showinfo("Bitti", "ROOT kapatıldı, Geant4 işlemi sonlandırıldı.")
                        process.terminate()  # Geant4'ü tamamen kapat

                    return
                time.sleep(1)
                timeout -= 1

            # ROOT dosyası hala yoksa hata ver
            messagebox.showerror("Hata", "ROOT dosyası bulunamadı!")

        threading.Thread(target=wait_and_open_root, daemon=True).start()

    except Exception as e:
        messagebox.showerror("Hata", str(e))

# Tkinter Arayüzü
root = tk.Tk()
root.title("Geant4 Simülasyonu")

tk.Label(root, text="Arrangement:").grid(row=0, column=0, padx=5, pady=5)
arrangement_entry = tk.Entry(root)
arrangement_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Type:").grid(row=1, column=0, padx=5, pady=5)
type_entry = tk.Entry(root)
type_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Geometry:").grid(row=2, column=0, padx=5, pady=5)
geometry_entry = tk.Entry(root)
geometry_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Thickness:").grid(row=3, column=0, padx=5, pady=5)
thickness_entry = tk.Entry(root)
thickness_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(root, text="Number of Sensors:").grid(row=4, column=0, padx=5, pady=5)
sensor_entry = tk.Entry(root)
sensor_entry.grid(row=4, column=1, padx=5, pady=5)

output_text = tk.Text(root, height=15, width=60)
output_text.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

run_button = tk.Button(root, text="Simülasyonu Çalıştır", command=run_simulation)
run_button.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
