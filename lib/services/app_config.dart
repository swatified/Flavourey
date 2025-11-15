import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static String get agoraAppId => dotenv.env['AGORA_APP_ID'] ?? '';
  static String get backendBaseUrl =>
      dotenv.env['BACKEND_BASE_URL'] ?? 'https://m5vdftcq-8000.inc1.devtunnels.ms/';

  static Future<void> load() async {
    await dotenv.load(fileName: '.env');
  }

  static void validate() {
    if (agoraAppId.isEmpty) {
      throw Exception('AGORA_APP_ID not found in .env file');
    }
  }
}
