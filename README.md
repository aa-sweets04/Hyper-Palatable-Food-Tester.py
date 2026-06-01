# HPF Scanner: A Hyper-Palatable Food Classifier

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![OpenCV](https://img.shields.io/badge/Built%20with-OpenCV-green)  ![Data](https://img.shields.io/badge/Data-OpenFoodFacts-orange)

A real-time barcode scanning tool that classifies food products as hyper-palatable using the quantitative framework developed by Fazzino et al. (2019). Point your webcam at any food barcode and instantly see whether it meets the scientific criteria for hyper-palatability.

---

## What is Hyper Palatable food?
Hyper-palatable food (HPF) refers to food items that have been formulated to exploit the psychological and physiological mechanisms that govern food intake and energy balance regulation. These foods are engineered — not merely tasty — in ways that override normal satiety signals.

Fazzino et al. (2019) developed the first quantitative definition of HPF, identifying three nutrient clusters that characterize these foods. This application uses those thresholds directly to classify products.

## The Three HPF Clusters

| Cluster | Criteria | Examples |
|---|---|---|
| **Fat + Sodium** | Fat > 25% of kcal AND sodium ≥ 0.30g/100g | Bacon, pizza, hot dogs |
| **Fat + Sugar** | Fat > 20% of kcal AND sugar > 20% of kcal | Ice cream, cake, cookies |
| **Carbs + Sodium** | Carbs > 40% of kcal AND sodium > 0.20g/100g | Crackers, pretzels, bread |

## Features 
* **Live Barcode Scanning:** Uses your computer's webcam to scan food barcodes (UPC/EAN).
* **Database Integration:** Automatically fetches live nutritional data from the OpenFoodFacts API.
* **HPF Clustering Logic:** Calculates macros per 100g and instantly categorizes the food into Fazzino's clusters (Fat & Sodium, Fat & Sugar, or Carbs & Sodium).

## Data Source
Nutritional data is fetched live from [Open Food Facts](https://world.openfoodfacts.org/), a free and open food product database maintained by volunteers. Not all products will be available, particularly regional or store-brand items.

## To Do
- ~~Connect the application to import HP information in a SQL database~~
- Rework current interface
- Transition to full web application

## References 
Fazzino, T. L., Rohde, K., & Sullivan, D. K. (2019). Hyper-Palatable Foods: Development of a Quantitative Definition and Application to the US Food System Database. Obesity, 27(11), 1761–1768.

## Limitations
* Applies to solid foods only — the research does not cover beverages
* Results depend on the accuracy of data in Open Food Facts, which is community-maintained
* This is a personal/educational project and is not medical or dietary advice
