import cv2
from pyzbar.pyzbar import decode
import requests
import time

# NUTRITIONAL LOGIC
def check_hyperpalatable(nutrients, product_name=""):
    fat_g = nutrients.get('fat_100g') or 0
    sugar_g = nutrients.get('sugars_100g') or 0
    carb_g = nutrients.get('carbohydrates_100g') or 0
    fiber_g = nutrients.get('fiber_100g') or 0
    sodium_g = nutrients.get('sodium_100g') or 0
    energy_kcal = nutrients.get('energy-kcal_100g') or 0

    # --- DEBUG: show what was actually received ---
    print(f"\n--- RAW NUTRIENTS for '{product_name}' ---")
    print(f"  Fat: {fat_g}g | Sugar: {sugar_g}g | Carbs: {carb_g}g | Fiber: {fiber_g}g | Sodium: {sodium_g}g | Calories: {energy_kcal}kcal")

    if energy_kcal == 0:
        # Try converting from kJ if kcal is missing
        energy_kj = nutrients.get('energy_100g') or 0
        if energy_kj > 0:
            energy_kcal = energy_kj / 4.184
            print(f"  (Converted from kJ: {energy_kj}kJ -> {energy_kcal:.1f}kcal)")
        else:
            print(">> RESULT: Unknown (No calorie data available for this product)")
            return

    # Math Conversions
    fat_kcal = fat_g * 9
    sugar_kcal = sugar_g * 4
    carb_kcal = carb_g * 4

    pct_fat_kcal = fat_kcal / energy_kcal
    pct_sugar_kcal = sugar_kcal / energy_kcal
    pct_carb_kcal = carb_kcal / energy_kcal
    pct_sodium_weight = sodium_g / 100

    print(f"--- BREAKDOWN: {pct_fat_kcal:.1%} Fat | {pct_sugar_kcal:.1%} Sugar | {pct_carb_kcal:.1%} Carbs | {pct_sodium_weight:.4f} Sodium ratio ---")

    is_hp = False
    if pct_fat_kcal > 0.25 and pct_sodium_weight >= 0.003:
        print(">> RESULT: HYPERPALATABLE (Fat + Sodium Cluster)")
        is_hp = True
    elif pct_fat_kcal > 0.20 and pct_sugar_kcal > 0.20:
        print(">> RESULT: HYPERPALATABLE (Fat + Sugar Cluster)")
        is_hp = True
    elif pct_carb_kcal > 0.40 and pct_sodium_weight > 0.002:
        print(">> RESULT: HYPERPALATABLE (Carbs + Sodium Cluster)")
        is_hp = True

    if not is_hp:
        print(">> RESULT: NOT HYPERPALATABLE")


def fetch_product_data(barcode_data):
    barcodes_to_try = [barcode_data, "0" + barcode_data]

    # Request ONLY the fields we need — faster and more reliable than v0
    FIELDS = "product_name,brands,nutriments"

    for barcode in barcodes_to_try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}?fields={FIELDS}"
        try:
            response = requests.get(
                url,
                timeout=5,
                headers={"User-Agent": "HPFScanner/1.0"}  # OFF docs recommend sending this
            )
            data = response.json()

            if data.get('status') == 1:
                product = data['product']
                product_name = f"{product.get('brands', 'N/A')} - {product.get('product_name', 'Unknown')}"
                print(f"\nFOUND: {product_name}")

                nutriments = product.get('nutriments', {})
                if not nutriments:
                    print(">> RESULT: Unknown (Product found but has no nutritional data)")
                    return True

                check_hyperpalatable(nutriments, product_name)
                return True

            else:
                print(f"  (Barcode {barcode} not found in database, status: {data.get('status_verbose', '?')})")

        except requests.exceptions.Timeout:
            print("  (Request timed out — check your connection)")
        except Exception as e:
            print(f"  (Error: {e})")

    print(">> RESULT: Unknown (Product not found in Open Food Facts)")
    return False


# Barcode Scanner
def start_scanner():
    cap = cv2.VideoCapture(0)
    last_barcode = None
    last_scan_time = 0
    print("Scanner Active. Press 'q' to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        detectedBarcodes = decode(frame)

        for barcode in detectedBarcodes:
            barcode_data = barcode.data.decode('utf-8')

            if barcode_data != last_barcode or (time.time() - last_scan_time > 5):
                print(f"\nScanned Barcode: {barcode_data}")
                fetch_product_data(barcode_data)

                last_barcode = barcode_data
                last_scan_time = time.time()

        cv2.imshow('HPF Scanner', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_scanner()