import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class UserProfile {
  String name;
  String email;
  String phone;
  String address;
  String profileImagePath;
  String dietPreference; // 'veg', 'non-veg', 'both'
  List<String> allergies;

  UserProfile({
    this.name = '',
    this.email = '',
    this.phone = '',
    this.address = '',
    this.profileImagePath = '',
    this.dietPreference = 'both',
    this.allergies = const [],
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
        'phone': phone,
        'address': address,
        'profileImagePath': profileImagePath,
        'dietPreference': dietPreference,
        'allergies': allergies,
      };

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
        name: json['name'] ?? '',
        email: json['email'] ?? '',
        phone: json['phone'] ?? '',
        address: json['address'] ?? '',
        profileImagePath: json['profileImagePath'] ?? '',
        dietPreference: json['dietPreference'] ?? 'both',
        allergies: List<String>.from(json['allergies'] ?? []),
      );
}

class UserProfileService extends ChangeNotifier {
  UserProfile _profile = UserProfile();
  Set<String> _favoriteDishes = {};

  UserProfile get profile => _profile;
  Set<String> get favoriteDishes => _favoriteDishes;

  bool isFavorite(String dishTitle) => _favoriteDishes.contains(dishTitle);

  Future<void> loadProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final profileJson = prefs.getString('userProfile');
    if (profileJson != null) {
      _profile = UserProfile.fromJson(json.decode(profileJson));
    }
    
    final favoritesJson = prefs.getString('favoriteDishes');
    if (favoritesJson != null) {
      _favoriteDishes = Set<String>.from(json.decode(favoritesJson));
    }
    notifyListeners();
  }

  Future<void> saveProfile() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('userProfile', json.encode(_profile.toJson()));
    notifyListeners();
  }

  Future<void> updateProfile({
    String? name,
    String? email,
    String? phone,
    String? address,
    String? profileImagePath,
    String? dietPreference,
    List<String>? allergies,
  }) async {
    if (name != null) _profile.name = name;
    if (email != null) _profile.email = email;
    if (phone != null) _profile.phone = phone;
    if (address != null) _profile.address = address;
    if (profileImagePath != null) _profile.profileImagePath = profileImagePath;
    if (dietPreference != null) _profile.dietPreference = dietPreference;
    if (allergies != null) _profile.allergies = allergies;
    
    await saveProfile();
  }

  Future<void> toggleFavorite(String dishTitle) async {
    if (_favoriteDishes.contains(dishTitle)) {
      _favoriteDishes.remove(dishTitle);
    } else {
      _favoriteDishes.add(dishTitle);
    }
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('favoriteDishes', json.encode(_favoriteDishes.toList()));
    notifyListeners();
  }

  Future<void> addAllergy(String allergy) async {
    if (!_profile.allergies.contains(allergy)) {
      _profile.allergies.add(allergy);
      await saveProfile();
    }
  }

  Future<void> removeAllergy(String allergy) async {
    _profile.allergies.remove(allergy);
    await saveProfile();
  }
}
