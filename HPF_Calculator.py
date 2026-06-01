def check_hyperpalatable(fat_g, sugar_g, carb_g, sodium_mg, fiber_g,
                          energy_kcal, total_weight_g):
    """
    Classify a food as hyperpalatable using Fazzino et al. (2019) criteria.

    Three clusters:
      1. Fat + Sodium  : fat > 25% of kcal  AND PSODI >= 0.30%
      2. Fat + Sugar   : fat > 20% of kcal  AND sugar > 20% of kcal
      3. Carbs + Sodium: net carbs > 40% of kcal AND PSODI >= 0.20%

    Parameters
    ----------
    fat_g           : grams of fat per serving
    sugar_g         : grams of sugar per serving
    carb_g          : grams of total carbohydrates per serving
    sodium_mg       : milligrams of sodium per serving  <- label units
    fiber_g         : grams of dietary fiber per serving
    energy_kcal     : total calories per serving
    total_weight_g  : total weight of the serving in grams

    Returns a dict with keys: result, cluster, breakdown
    """

    # unit conversion: mg -> g (paper works in grams) 
    sodium_g = sodium_mg / 1000

    # gram-to-kcal conversions 
    fat_kcal      = fat_g   * 9    # fat:   9 kcal/g
    sugar_kcal    = sugar_g * 4    # sugar: 4 kcal/g (it's a carbohydrate)

    # Net carbs strips out fiber (not digested) and sugar (its own cluster variable)
    net_carb_g    = max(carb_g - fiber_g - sugar_g, 0)
    net_carb_kcal = net_carb_g * 4

    # percentage calculations 
    pct_fat   = fat_kcal      / energy_kcal   # fat as share of total calories
    pct_sugar = sugar_kcal    / energy_kcal   # sugar as share of total calories
    pct_carb  = net_carb_kcal / energy_kcal   # net carbs as share of total calories

    psodi = (sodium_g / total_weight_g) * 100

    breakdown = [
        f"Serving weight  {total_weight_g:.1f} g",
        f"Calories        {energy_kcal:.0f} kcal",
        f"Fat             {pct_fat:.1%} of kcal  (threshold: >25% FSOD cluster, >20% FS cluster)",
        f"Sugar           {pct_sugar:.1%} of kcal  (threshold: >20%)",
        f"Net Carbs       {pct_carb:.1%} of kcal  (threshold: >40%)",
        f"PSODI           {psodi:.4f}%        (threshold: >=0.30% FSOD, >=0.20% CSOD)",
    ]

    # cluster checks

    matched_clusters = []
 
    if pct_fat > 0.25 and psodi >= 0.30:
        matched_clusters.append('Fat + Sodium (FSOD)')
    if pct_fat > 0.20 and pct_sugar > 0.20:
        matched_clusters.append('Fat + Sugar (FS)')
    if pct_carb > 0.40 and psodi >= 0.20:
        matched_clusters.append('Carbs + Sodium (CSOD)')
 
    if matched_clusters:
        return {'result': 'HYPERPALATABLE', 'clusters': matched_clusters, 'breakdown': breakdown}
 
    return {'result': 'NOT HYPERPALATABLE', 'clusters': [], 'breakdown': breakdown}


def main():
    print("=== HPF Application V2 ===")
    print("Enter nutritional values from the food label for one serving.\n")
    print("Tip: 'Serving size' on US labels is given in grams (e.g., '28g / 1 oz').\n")

    try:
        fat_g          = float(input("Fat (g):               "))
        sugar_g        = float(input("Sugar (g):             "))
        carb_g         = float(input("Carbohydrates (g):     "))
        sodium_mg      = float(input("Sodium (mg):           ")) 
        fiber_g        = float(input("Fiber (g):             "))
        energy_kcal    = float(input("Total Calories (kcal): "))
        total_weight_g = float(input("Serving weight (g):    "))
    except ValueError:
        print("Invalid input -- please enter numbers only.")
        return

    # Division by zero checks
    if energy_kcal <= 0:
        print("Calories must be greater than 0.")
        return
    if total_weight_g <= 0:
        print("Serving weight must be greater than 0.")
        return

    result = check_hyperpalatable(
        fat_g, sugar_g, carb_g, sodium_mg, fiber_g, energy_kcal, total_weight_g
    )

    print("\n--- Nutritional Breakdown ---")
    for line in result['breakdown']:
        print(" ", line)
 
    print(f"\n>> RESULT: {result['result']}")
    if result['clusters']:
        for cluster in result['clusters']:
            print(f"   Cluster: {cluster}")


if __name__ == "__main__":
    main()