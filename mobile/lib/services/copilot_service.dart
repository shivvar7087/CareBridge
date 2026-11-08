import '../core/api_client.dart';
import '../models/emergency_card.dart';
import '../models/medication.dart';

class CopilotService {
  final ApiClient _client = ApiClient();

  Future<String> askCopilot(String query) async {
    final response = await _client.post('/copilot/ask', {'query': query});
    return response['answer'] as String? ?? 'No response received.';
  }

  Future<EmergencyCardData> getEmergencyCard() async {
    final response = await _client.get('/copilot/emergency-card');
    return EmergencyCardData.fromJson(response as Map<String, dynamic>);
  }

  Future<void> sendEmergencySos() async {
    await _client.post('/copilot/emergency-sos');
  }

  Future<MedicationScheduleResponse> getMedications() async {
    final response = await _client.get('/copilot/medications');
    return MedicationScheduleResponse.fromJson(response as Map<String, dynamic>);
  }

  Future<void> logMedication(String id, bool taken) async {
    await _client.post('/copilot/medications/log', {
      'medication_id': id,
      'taken': taken,
    });
  }

  Future<MedicationItem> addMedication(Map<String, dynamic> data) async {
    final response = await _client.post('/copilot/medications', data);
    return MedicationItem.fromJson(response['medication'] as Map<String, dynamic>);
  }

  Future<MedicationItem> updateMedication(String id, Map<String, dynamic> data) async {
    final response = await _client.put('/copilot/medications/$id', data);
    return MedicationItem.fromJson(response['medication'] as Map<String, dynamic>);
  }

  Future<void> deleteMedication(String id) async {
    await _client.delete('/copilot/medications/$id');
  }
}

