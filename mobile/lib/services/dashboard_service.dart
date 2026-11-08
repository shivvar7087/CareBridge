import '../core/api_client.dart';

class DashboardService {
  final ApiClient _client = ApiClient();

  Future<Map<String, dynamic>> getDashboard() async {
    final response = await _client.get('/dashboard');
    return response as Map<String, dynamic>;
  }
}

