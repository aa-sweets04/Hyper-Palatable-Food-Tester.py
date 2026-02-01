import requests

def run_scanner():
    barcode = input("Enter a barcode: ").strip()
    
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    print(f"Dialing {url}...")
    
    try:

        response = requests.get(url, timeout=10) 
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 1:
                product = data['product']
                nutriments = product.get('nutriments', {})

                print(f"\nFOUND: {product.get('product_name')}")
                print(f"Brand: {product.get('brands')}")

                print("\n--- Data PER 100g ---")
                print(f"Fat: {nutriments.get('fat_100g')} g")
                print(f"Sugar: {nutriments.get('sugars_100g')} g")
                print(f"Carbs: {nutriments.get('carbohydrates_100g')} g")
                print(f"Sodium: {nutriments.get('sodium_100g')} g")
                print(f"Calories: {nutriments.get('energy-kcal_100g')} kcal")
            
            else:
                print(f"Connection worked, but product {barcode} is not in the database.")
                print(f"Status message: {data.get('status_verbose')}")
        
        else:
            print(f"Server Error. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Internet Connection Error: {e}")

if __name__ == "__main__":
    run_scanner()