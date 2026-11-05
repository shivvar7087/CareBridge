class EmergencyCardData {
  final String fullName;
  final String phone;
  final String dateOfBirth;
  final String bloodGroup;
  final List<String> allergies;
  final List<String> chronicConditions;
  final String hospitalName;
  final String primaryPhysician;
  final String hospitalHelpline;
  final String emergencyNotes;
  final List<EmergencyCaregiver> caregivers;
  final List<String> medications;
  final String lastUpdated;

  EmergencyCardData({
    required this.fullName,
    required this.phone,
    required this.dateOfBirth,
    required this.bloodGroup,
    required this.allergies,
    required this.chronicConditions,
    required this.hospitalName,
    required this.primaryPhysician,
    required this.hospitalHelpline,
    required this.emergencyNotes,
    required this.caregivers,
    required this.medications,
    required this.lastUpdated,
  });

  factory EmergencyCardData.fromJson(Map<String, dynamic> json) {
    final p = json['patient'] as Map<String, dynamic>? ?? {};
    final cgList = (json['caregivers'] as List<dynamic>? ?? [])
        .map((e) => EmergencyCaregiver.fromJson(e as Map<String, dynamic>))
        .toList();
    final medList = (json['medications'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();
    final allList = (p['allergies'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();
    final condList = (p['chronic_conditions'] as List<dynamic>? ?? [])
        .map((e) => e.toString())
        .toList();

    return EmergencyCardData(
      fullName: p['full_name'] as String? ?? 'Patient',
      phone: p['phone'] as String? ?? 'Not provided',
      dateOfBirth: p['date_of_birth'] as String? ?? '',
      bloodGroup: p['blood_group'] as String? ?? 'Unknown',
      allergies: allList,
      chronicConditions: condList,
      hospitalName: p['hospital_name'] as String? ?? 'Harborview Medical Centre',
      primaryPhysician: p['primary_physician'] as String? ?? 'Attending Clinician',
      hospitalHelpline: p['hospital_helpline'] as String? ?? '',
      emergencyNotes: p['emergency_notes'] as String? ?? '',
      caregivers: cgList,
      medications: medList,
      lastUpdated: json['last_updated'] as String? ?? 'Recently',
    );
  }
}

class EmergencyCaregiver {
  final String name;
  final String email;
  final String phone;
  final String relation;

  EmergencyCaregiver({
    required this.name,
    required this.email,
    required this.phone,
    required this.relation,
  });

  factory EmergencyCaregiver.fromJson(Map<String, dynamic> json) {
    return EmergencyCaregiver(
      name: json['name'] as String? ?? 'Caregiver',
      email: json['email'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      relation: json['relation'] as String? ?? 'Family Contact',
    );
  }
}
