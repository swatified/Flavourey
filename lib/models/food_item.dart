class FoodItem {
  final String title;
  final String cuisine;
  final List<String> ingredients;
  final String imageUrl;
  final int priceInr;

  FoodItem({
    required this.title,
    required this.cuisine,
    required this.ingredients,
    required this.imageUrl,
    required this.priceInr,
  });

  factory FoodItem.fromCsv(List<dynamic> row) {
    return FoodItem(
      title: row[0].toString(),
      cuisine: row[1].toString(),
      ingredients: row[2].toString().split(',').map((e) => e.trim()).toList(),
      imageUrl: row[3].toString(),
      priceInr: int.tryParse(row[4].toString()) ?? 0,
    );
  }
}
