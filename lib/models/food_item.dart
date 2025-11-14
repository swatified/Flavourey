class FoodItem {
  final String title;
  final String cuisine;
  final List<String> ingredients;
  final String imageUrl;
  final int priceInr;
  final double rating;
  final int calories;
  final String dietType;

  FoodItem({
    required this.title,
    required this.cuisine,
    required this.ingredients,
    required this.imageUrl,
    required this.priceInr,
    required this.rating,
    required this.calories,
    required this.dietType,
  });

  factory FoodItem.fromCsv(List<dynamic> row) {
    // CSV expected columns (in order):
    // title, type-of-cuisine, ingredients, image-url, price_inr, rating, calories, diet_type
    double parsedRating = 0.0;
    int parsedCalories = 0;
    String parsedDietType = 'Veg';
    
    try {
      if (row.length > 5) {
        parsedRating = double.tryParse(row[5].toString()) ?? 0.0;
      }
    } catch (_) {
      parsedRating = 0.0;
    }

    try {
      if (row.length > 6) {
        parsedCalories = int.tryParse(row[6].toString()) ?? 0;
      }
    } catch (_) {
      parsedCalories = 0;
    }

    try {
      if (row.length > 7) {
        parsedDietType = row[7].toString();
      }
    } catch (_) {
      parsedDietType = 'Veg';
    }

    return FoodItem(
      title: row[0].toString(),
      cuisine: row[1].toString(),
      ingredients: row[2].toString().split(',').map((e) => e.trim()).toList(),
      imageUrl: row[3].toString(),
      priceInr: int.tryParse(row[4].toString()) ?? 0,
      rating: parsedRating,
      calories: parsedCalories,
      dietType: parsedDietType,
    );
  }
}
