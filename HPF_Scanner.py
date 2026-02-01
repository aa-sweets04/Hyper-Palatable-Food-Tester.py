import requests

# THE BRAIN OF THE HPF SCANNER
def check_hyperpalatable(nutrients):
    # Data Extraction
    fat_g = nutrients.get('fat_100g', 0)
    sugar_g = nutrients.get('sugars_100g', 0)
    carb_g = nutrients.get('carbohydrates_100g', 0)
    sodium_g = nutrients.get('sodium_100g', 0)
    energy_kcal = nutrients.get('energy-kcal_100g', 0)

    if energy_kcal == 0:
        print("RESULT: Unknown (Calories are 0 or missing)")
        return

    # Math Conversion
    fat_kcal = fat_g * 9
    sugar_kcal = sugar_g * 4
    carb_kcal = carb_g * 4

    pct_fat_kcal = fat_kcal / energy_kcal
    pct_sugar_kcal = sugar_kcal / energy_kcal
    pct_carb_kcal = carb_kcal / energy_kcal
    pct_sodium_weight = sodium_g / 100 

    # DEBUG OUTPUT
    print("\n--- NUTRITIONAL BREAKDOWN ---")
    print(f"Fat: {pct_fat_kcal:.1%} of calories")
    print(f"Sugar: {pct_sugar_kcal:.1%} of calories")
    print(f"Carbs: {pct_carb_kcal:.1%} of calories")
    print(f"Sodium: {pct_sodium_weight:.2%} of weight")
    print("-" * 30)

    #HPF LOGIC and CLASSIFICATION
    is_hp = False

    if pct_fat_kcal > 0.25 and pct_sodium_weight >= 0.003:
        print("RESULT: HYPERPALATABLE FOOD (Fat and Sodium cluster)")
        is_hp = True
    if pct_fat_kcal > 0.20 and pct_sugar_kcal > 0.20:
        print("RESULT: HYPERPALATABLE FOOD (Fat and Sugar cluster)")
        is_hp = True
    if pct_carb_kcal > 0.40 and pct_sodium_weight > 0.002:
        print("RESULT: HYPERPALATABLE FOOD (Carbohydrates and Sodium cluster)")
        is_hp = True

    if not is_hp:
        print("RESULT: NOT A HYPERPALATABLE FOOD")


#  Openfoodfacts nutritonal fetcher
def run_app():
    print("\n=== HYPERPALATABLE FOOD SCANNER ===")
    user_input = input("Scan/Type Barcode: ").strip()
    
    barcodes_to_try = [user_input, "0" + user_input]
    
    product_found = False
    
    print(f"Searching database...")

    for barcode in barcodes_to_try:
        if product_found: break 
            
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get('status') == 1:
                product_found = True
                product = data['product']
                name = product.get('product_name', 'Unknown Name')
                brand = product.get('brands', 'Unknown Brand')
                
                print(f"FOUND: {brand} - {name}")
                
            
                nutrients = product.get('nutriments', {})
                check_hyperpalatable(nutrients)
        
        except Exception:
            pass 

    if not product_found:
        print(f"Product not found. (Tried {user_input} and 0{user_input})")

if __name__ == "__main__":
    run_app()