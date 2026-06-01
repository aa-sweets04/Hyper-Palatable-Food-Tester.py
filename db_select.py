import sqlite3

conn = sqlite3.connect('food_history.db')
cursor = conn.cursor()

select_query = "SELECT * FROM scanned_foods WHERE barcode = ?"

search_barcode = "0123456789012"

cursor.execute(select_query, (search_barcode,))

result = cursor.fetchone()

conn.close()

if result:
    print("Food found in the database:")
    print(f"Name: {result[1]}")
    print(f"Status: {result[8]}")
else:
    print("Barcode not found. Time to check OpenFoodFacts!")
