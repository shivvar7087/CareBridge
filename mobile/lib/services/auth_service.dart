import '../core/api_client.dart';
import '../core/constants.dart';

class AuthService {
  final ApiClient _client = ApiClient();

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _client.post('/auth/token', {
      'username': email,
      'password': password,
    });
    final token = response['access_token'] as String;
    final user = response['user'] as Map<String, dynamic>;
    _client.setAuth(token, user);
    return user;
  }

  Future<Map<String, dynamic>> loginDemo() async {
    return login(AppConstants.demoEmail, AppConstants.demoPassword);
  }

  void logout() {
    _client.clearAuth();
  }
}

