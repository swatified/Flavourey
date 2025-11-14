import 'package:flutter/foundation.dart';
import '../models/food_item.dart';

class CartItem {
  final FoodItem item;
  int quantity;

  CartItem({required this.item, this.quantity = 1});

  double get subtotal => item.priceInr * quantity.toDouble();
}

class CartService extends ChangeNotifier {
  final Map<String, CartItem> _items = {};

  List<CartItem> get items => _items.values.toList();

  int get totalItems => _items.values.fold(0, (s, e) => s + e.quantity);

  double get totalPrice => _items.values.fold(0.0, (s, e) => s + e.subtotal);

  int get totalCalories => _items.values.fold(0, (s, e) => s + (e.item.calories * e.quantity));

  int getItemQuantity(String title) {
    return _items.containsKey(title) ? _items[title]!.quantity : 0;
  }

  void addItem(FoodItem food, {int quantity = 1}) {
    final key = food.title;
    if (_items.containsKey(key)) {
      _items[key]!.quantity += quantity;
    } else {
      _items[key] = CartItem(item: food, quantity: quantity);
    }
    notifyListeners();
  }

  void removeItem(String title) {
    _items.remove(title);
    notifyListeners();
  }

  void increment(String title) {
    if (_items.containsKey(title)) {
      _items[title]!.quantity++;
      notifyListeners();
    }
  }

  void decrement(String title) {
    if (_items.containsKey(title)) {
      final ci = _items[title]!;
      if (ci.quantity > 1) {
        ci.quantity--;
      } else {
        _items.remove(title);
      }
      notifyListeners();
    }
  }

  void clear() {
    _items.clear();
    notifyListeners();
  }
}
