from unittest import result

import cv2
from pyzbar.pyzbar import decode
import requests
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
import sqlite3

COLORS = {
    'bg':      "#0f0f0f",
    'panel':   "#1a1a1a",
    'border':  "#2a2a2a",
    'green':   "#00c896",
    'red':     "#ff4d4d",
    'primary': "#f0f0f0",
    'muted':   "#666666",
    'mono':    "#a8d8a8",
}


# Nutritional logic 

def classify(nutrients):
    fat_g       = nutrients.get('fat_g')       or 0
    sugar_g     = nutrients.get('sugar_g')     or 0
    carb_g      = nutrients.get('carb_g')      or 0
    fiber_g     = nutrients.get('fiber_g')     or 0
    sodium_g    = nutrients.get('sodium_g')    or 0
    energy_kcal = nutrients.get('energy_kcal') or 0

    if energy_kcal == 0:
        return {'result': 'Unknown', 'cluster': '', 'breakdown': ['No calorie data']}

    pct_fat   = (fat_g * 9)                          / energy_kcal
    pct_sugar = (sugar_g * 4)                        / energy_kcal
    pct_carb  = (max(carb_g - fiber_g - sugar_g, 0) * 4) / energy_kcal
    pct_sod   = sodium_g / 100

    breakdown = [
        f"Calories  {energy_kcal:.0f} kcal / 100g",
        f"Fat       {pct_fat:.1%}",
        f"Sugar     {pct_sugar:.1%}",
        f"Net Carbs {pct_carb:.1%}",
        f"Sodium    {pct_sod:.4f}",
    ]

    if pct_fat > 0.25 and pct_sod >= 0.003:
        return {'result': 'HYPERPALATABLE', 'cluster': 'Fat + Sodium', 'breakdown': breakdown}
    if pct_fat > 0.20 and pct_sugar > 0.20:
        return {'result': 'HYPERPALATABLE', 'cluster': 'Fat + Sugar',  'breakdown': breakdown}
    if pct_carb > 0.40 and pct_sod >= 0.002:
        return {'result': 'HYPERPALATABLE', 'cluster': 'Carbs + Sodium', 'breakdown': breakdown}

    return {'result': 'NOT HYPERPALATABLE', 'cluster': '', 'breakdown': breakdown}


# Open Food Facts lookup 

def fetch(barcode):
    for code in [barcode, "0" + barcode]:
        try:
            r = requests.get(
                f"https://world.openfoodfacts.org/api/v2/product/{code}?fields=product_name,brands,nutriments",
                timeout=5, headers={"User-Agent": "HPFScanner/4.0"}
            ).json()

            if r.get('status') == 1:
                p  = r['product']
                nm = r['product'].get('nutriments', {})
                if not nm:
                    return None

                kcal = nm.get('energy-kcal_100g') or (nm.get('energy_100g') or 0) / 4.184
                return {
                    'name':        f"{p.get('brands', '')} {p.get('product_name', '')}".strip(),
                    'fat_g':       nm.get('fat_100g')           or 0,
                    'sugar_g':     nm.get('sugars_100g')        or 0,
                    'carb_g':      nm.get('carbohydrates_100g') or 0,
                    'fiber_g':     nm.get('fiber_100g')         or 0,
                    'sodium_g':    nm.get('sodium_100g')        or 0,
                    'energy_kcal': kcal,
                }
        except Exception:
            pass
    return None


# HPF App

class HPFScanner:
    def __init__(self, win):
        self.win     = win
        self.running = True
 
        self.last_result = None
 
        win.title("HPF Scanner")
        win.geometry("860x520")
        win.resizable(False, False)
        win.configure(bg=COLORS['bg'])
        win.protocol("WM_DELETE_WINDOW", self.close)
 
        self._build()
        threading.Thread(target=self._scan_loop, daemon=True).start()
 
    def _build(self):
        self.cam_label = tk.Label(self.win, bg=COLORS['border'])
        self.cam_label.place(x=20, y=20, width=500, height=480)
 
        rx = 540
        tk.Label(self.win, text="HPF SCANNER", bg=COLORS['bg'], fg=COLORS['primary'], font=("Helvetica", 14, "bold")).place(x=rx, y=20)
 
        self.name_var = tk.StringVar(value="—")
        tk.Label(self.win, textvariable=self.name_var, bg=COLORS['bg'], fg=COLORS['primary'], font=("Helvetica", 10), wraplength=290, justify="left").place(x=rx, y=60)
 
        self.result_var = tk.StringVar(value="—")
        self.result_lbl = tk.Label(self.win, textvariable=self.result_var, bg=COLORS['bg'], fg=COLORS['muted'], font=("Helvetica", 13, "bold"))
        self.result_lbl.place(x=rx, y=110)
 
        self.cluster_var = tk.StringVar(value="")
        tk.Label(self.win, textvariable=self.cluster_var, bg=COLORS['bg'], fg=COLORS['muted'], font=("Helvetica", 10)).place(x=rx, y=140)
 
        self.breakdown = tk.Text(self.win, bg=COLORS['panel'], fg=COLORS['mono'], font=("Helvetica", 11), width=30, height=7, relief="flat", padx=10, pady=8, state="disabled", cursor="arrow")
        self.breakdown.place(x=rx, y=175)
 
        self.status_var = tk.StringVar(value="● SCANNING")
        tk.Label(self.win, textvariable=self.status_var, bg=COLORS['bg'], fg=COLORS['green'], font=("Helvetica", 9)).place(x=rx, y=450)
 
    def _set_results(self, name, result, cluster, breakdown_lines):
        self.name_var.set(name)
        self.result_var.set(result)
        self.cluster_var.set(f"Cluster: {cluster}" if cluster else "")
        color = COLORS['red'] if result == 'HYPERPALATABLE' else COLORS['green']
        self.result_lbl.config(fg=color)
 
        self.breakdown.config(state="normal")
        self.breakdown.delete("1.0", tk.END)
        for line in breakdown_lines:
            self.breakdown.insert(tk.END, line + "\n")
        self.breakdown.config(state="disabled")
 
    def _draw_barcode_box(self, frame, barcode):
        if self.last_result == 'HYPERPALATABLE':
            color = (80, 80, 255)    
        elif self.last_result == 'NOT HYPERPALATABLE':
            color = (150, 200, 80)   
        else:
            color = (80, 220, 220)   
 
        import numpy as np
        pts = np.array([[p.x, p.y] for p in barcode.polygon], dtype=np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)
 
    def _scan_loop(self):
        cap            = cv2.VideoCapture(0)
        last_barcode   = None
        last_scan_time = 0
 
        while self.running and cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
 
            frame    = cv2.flip(frame, 1)
            detected = decode(frame)
 
            for bc in detected:
                self._draw_barcode_box(frame, bc)
 
                data = bc.data.decode('utf-8')
                if data != last_barcode or time.time() - last_scan_time > 5:
                    last_barcode   = data
                    last_scan_time = time.time()
 
 
                    self.last_result = None   # reset to yellow box while fetching
                    self.win.after(0, self.status_var.set, "● PROCESSING...")

                    #connection to sqlite database
                    conn = sqlite3.connect('food_history.db')
                    cursor = conn.cursor()

                    cursor.execute("SELECT * FROM scanned_foods WHERE barcode = ?", (data,))
                    local_food = cursor.fetchone()

                    if local_food is not None:
                        print(f"food found in database: {local_food[1]}")
                        nutrients = {
                            'name': local_food[1],
                            'energy_kcal': local_food[2],
                            'fat_g': local_food[3],
                            'sugar_g': local_food[4],
                            'carb_g': local_food[5],
                            'fiber_g': local_food[6],
                            'sodium_g': local_food[7],
                        }

                        c = classify(nutrients)
                        self.last_result = c['result']
                        self.win.after(0, self._set_results, nutrients['name'], c['result'], c['cluster'], c['breakdown'])
                    else:
                        print("Barcode not found. Checking OpenFoodFacts...")

                        nutrients = fetch(data)
                        if nutrients:
                            c = classify(nutrients)
                            self.last_result = c['result']
                            self.win.after(0, self._set_results, nutrients['name'], c['result'], c['cluster'], c['breakdown'])

                            db_save = sqlite3.connect('food_history.db')
                            cursor_save = db_save.cursor()
                            insert_query = """
                            INSERT OR IGNORE INTO scanned_foods (barcode, product_name, calories, fat_g, sugar_g, carb_g, fiber_g, sodium_g, hpf_status, hpf_cluster)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """
                            food_data = (
                                data,
                                nutrients['name'],
                                nutrients['energy_kcal'],
                                nutrients['fat_g'],
                                nutrients['sugar_g'],
                                nutrients['carb_g'],
                                nutrients['fiber_g'],
                                nutrients['sodium_g'],
                                c['result'],
                                c['cluster']
                            )

                            cursor_save.execute(insert_query, food_data)
                            db_save.commit()
                            db_save.close()
                        else:
                            self.last_result = None
                            self.win.after(0, self._set_results, data, "Not found", "", [])

                    conn.close()
                    self.win.after(0, self.status_var.set, "● SCANNING")

 
                    nutrients = fetch(data)
                    if nutrients:
                        c = classify(nutrients)
                        self.last_result = c['result']
                        self.win.after(0, self._set_results,nutrients['name'], c['result'], c['cluster'], c['breakdown'])
                    else:
                        self.last_result = None
                        self.win.after(0, self._set_results, data, "Not found", "", [])
 
                    self.win.after(0, self.status_var.set, "● SCANNING")
 
            img   = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((500, 480))
            photo = ImageTk.PhotoImage(image=img)
            self.cam_label.photo = photo
            self.win.after(0, self.cam_label.config, {"image": photo})
 
            time.sleep(0.03)
 
        cap.release()
 
    def close(self):
        self.running = False
        time.sleep(0.1)
        self.win.destroy()
 
 
if __name__ == "__main__":
    conn = sqlite3.connect("food_history.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scanned_foods (
        barcode TEXT PRIMARY KEY,
        product_name TEXT,
        calories REAL,
        fat_g REAL,
        sugar_g REAL,
        carb_g REAL,
        fiber_g REAL,
        sodium_g REAL,
        hpf_status TEXT,
        hpf_cluster TEXT
    );
    """)
    
    conn.commit()
    conn.close()

    win = tk.Tk()
    HPFScanner(win)
    win.mainloop()