import sqlite3

conn = sqlite3.connect("food_history.db")
cursor = conn.cursor()

insert_query = """
INSERT OR IGNORE INTO scanned_foods (barcode, product_name, calories, fat_g, sugar_g, carb_g, fiber_g, sodium_g, hpf_status, hpf_cluster)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

mock_data = (
    "0123456789012", 
    "Mock Chocolate Chip Cookie", 
    150.0, 
    8.0, 
    12.0, 
    20.0, 
    1.0, 
    0.1, 
    "HYPERPALATABLE", 
    "Fat + Sugar"
)

cursor.execute(insert_query, mock_data)

conn.commit()
conn.close()

print("Mock food saved to the database successfully.")

