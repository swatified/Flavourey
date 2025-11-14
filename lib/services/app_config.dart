import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static String get agoraAppId => dotenv.env['AGORA_APP_ID'] ?? '';
  static String get backendBaseUrl =>
      dotenv.env['BACKEND_BASE_URL'] ?? 'http://localhost:8000';

  static Future<void> load() async {
    await dotenv.load(fileName: '.env');
  }

  static void validate() {
    if (agoraAppId.isEmpty) {
      throw Exception('AGORA_APP_ID not found in .env file');
    }
  }
}
