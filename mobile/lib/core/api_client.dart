import 'dart:convert';
import 'package:http/http.dart' as http;
import 'constants.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  String baseUrl = AppConstants.defaultApiUrl;
  String? authToken;
  Map<String, dynamic>? currentUser;

  void setAuth(String token, Map<String, dynamic> user) {
    authToken = token;
    currentUser = user;
  }

  void clearAuth() {
    authToken = null;
    currentUser = null;
  }

  bool get isAuthenticated => authToken != null;

  Map<String, String> _headers() {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (authToken != null) {
      headers['Authorization'] = 'Bearer $authToken';
    }
    return headers;
  }

  Future<dynamic> get(String endpoint) async {
    return _safeRequest(() {
      final uri = Uri.parse('$baseUrl$endpoint');
      return http.get(uri, headers: _headers());
    });
  }

  Future<dynamic> post(String endpoint, [Map<String, dynamic>? body]) async {
    return _safeRequest(() {
      final uri = Uri.parse('$baseUrl$endpoint');
      return http.post(
        uri,
        headers: _headers(),
        body: body != null ? jsonEncode(body) : null,
      );
    });
  }

  Future<dynamic> put(String endpoint, [Map<String, dynamic>? body]) async {
    return _safeRequest(() {
      final uri = Uri.parse('$baseUrl$endpoint');
      return http.put(
        uri,
        headers: _headers(),
        body: body != null ? jsonEncode(body) : null,
      );
    });
  }

  Future<dynamic> patch(String endpoint, [Map<String, dynamic>? body]) async {
    return _safeRequest(() {
      final uri = Uri.parse('$baseUrl$endpoint');
      return http.patch(
        uri,
        headers: _headers(),
        body: body != null ? jsonEncode(body) : null,
      );
    });
  }

  Future<dynamic> delete(String endpoint) async {
    return _safeRequest(() {
      final uri = Uri.parse('$baseUrl$endpoint');
      return http.delete(uri, headers: _headers());
    });
  }

  Future<dynamic> _safeRequest(Future<http.Response> Function() req) async {
    try {
      final response = await req();
      return _handleResponse(response);
    } on http.ClientException catch (e) {
      if (e.message.toLowerCase().contains('failed to fetch')) {
        throw ApiException(
          'Unable to connect to $baseUrl. This happens when the Render server is waking up, or browser CORS blocks Chrome. Try Windows desktop (`flutter run -d windows`) or local server.',
          0,
        );
      }
      throw ApiException('Network error: ${e.message}', 0);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Connection error: $e', 0);
    }
  }

  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    } else {
      String message = 'Request failed (${response.statusCode})';
      try {
        final err = jsonDecode(response.body);
        if (err is Map && err.containsKey('detail')) {
          message = err['detail'].toString();
        }
      } catch (_) {}
      throw ApiException(message, response.statusCode);
    }
  }
}

class ApiException implements Exception {
  final String message;
  final int statusCode;
  ApiException(this.message, this.statusCode);

  @override
  String toString() => message;
}

