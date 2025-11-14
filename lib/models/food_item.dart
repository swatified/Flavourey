class FoodItem {
  final String title;
  final String cuisine;
  final List<String> ingredients;
  final String imageUrl;
  final int priceInr;
  final double rating;

  FoodItem({
    required this.title,
    required this.cuisine,
    required this.ingredients,
    required this.imageUrl,
    required this.priceInr,
    required this.rating,
  });

  factory FoodItem.fromCsv(List<dynamic> row) {
    // CSV expected columns (in order):
    // title, type-of-cuisine, ingredients, image-url, price_inr, rating
    double parsedRating = 0.0;
    try {
      if (row.length > 5) {
        parsedRating = double.tryParse(row[5].toString()) ?? 0.0;
      }
    } catch (_) {
      parsedRating = 0.0;
    }

    return FoodItem(
      title: row[0].toString(),
      cuisine: row[1].toString(),
      ingredients: row[2].toString().split(',').map((e) => e.trim()).toList(),
      imageUrl: row[3].toString(),
      priceInr: int.tryParse(row[4].toString()) ?? 0,
      rating: parsedRating,
    );
  }
}
