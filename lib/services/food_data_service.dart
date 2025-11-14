import 'package:flutter/services.dart';
import 'package:csv/csv.dart';
import '../models/food_item.dart';

class FoodDataService {
  static List<FoodItem>? _cachedFoodItems;

  static Future<List<FoodItem>> loadFoodItems() async {
    if (_cachedFoodItems != null) {
      return _cachedFoodItems!;
    }

    try {
      final csvString = await rootBundle.loadString('assets/dataset/Indian-Food-Dataset.csv');
      List<List<dynamic>> csvTable = const CsvToListConverter().convert(csvString);
      
      // Skip header row
      _cachedFoodItems = csvTable.skip(1).map((row) {
        return FoodItem.fromCsv(row);
      }).toList();

      return _cachedFoodItems!;
    } catch (e) {
      // Error loading food items
      return [];
    }
  }

  static Map<String, List<FoodItem>> groupByCuisine(List<FoodItem> items) {
    final Map<String, List<FoodItem>> grouped = {};
    
    for (var item in items) {
      if (!grouped.containsKey(item.cuisine)) {
        grouped[item.cuisine] = [];
      }
      grouped[item.cuisine]!.add(item);
    }
    
    return grouped;
  }
}
