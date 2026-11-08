import '../core/api_client.dart';
import '../models/journey_task.dart';

class JourneyService {
  final ApiClient _client = ApiClient();

  Future<List<JourneyTask>> getTimeline() async {
    final response = await _client.get('/journey/timeline');
    if (response is List) {
      return response.map((item) => JourneyTask.fromJson(item as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<List<JourneyTask>> getTasks([String? status]) async {
    final endpoint = status != null && status != 'All' ? '/tasks?status=$status' : '/tasks';
    final response = await _client.get(endpoint);
    if (response is List) {
      return response.map((item) => JourneyTask.fromJson(item as Map<String, dynamic>)).toList();
    }
    return [];
  }

  Future<JourneyTask> updateTaskStatus(int taskId, String status) async {
    final response = await _client.patch('/tasks/$taskId/status', {'status': status});
    return JourneyTask.fromJson(response as Map<String, dynamic>);
  }

  Future<JourneyTask> createTask(Map<String, dynamic> data) async {
    final response = await _client.post('/tasks', data);
    return JourneyTask.fromJson(response as Map<String, dynamic>);
  }
}

