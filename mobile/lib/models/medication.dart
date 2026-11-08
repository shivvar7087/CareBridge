class MedicationItem {
  final String id;
  final String name;
  final String dosage;
  final String timeSlot;
  final String timeLabel;
  final String instructions;
  final String indication;
  bool taken;

  MedicationItem({
    required this.id,
    required this.name,
    required this.dosage,
    required this.timeSlot,
    required this.timeLabel,
    required this.instructions,
    required this.indication,
    this.taken = false,
  });

  factory MedicationItem.fromJson(Map<String, dynamic> json) {
    return MedicationItem(
      id: json['id'].toString(),
      name: json['name'] as String? ?? 'Prescription',
      dosage: json['dosage'] as String? ?? '',
      timeSlot: json['time_slot'] as String? ?? 'Morning',
      timeLabel: json['time_label'] as String? ?? '08:00 AM',
      instructions: json['instructions'] as String? ?? '',
      indication: json['indication'] as String? ?? '',
      taken: json['taken'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'dosage': dosage,
      'time_slot': timeSlot,
      'time_label': timeLabel,
      'instructions': instructions,
      'indication': indication,
    };
  }
}

class MedicationScheduleResponse {
  final String today;
  final int streakDays;
  final int totalDoses;
  final int completedDoses;
  final int adherencePercentage;
  final List<MedicationItem> schedule;

  MedicationScheduleResponse({
    required this.today,
    required this.streakDays,
    required this.totalDoses,
    required this.completedDoses,
    required this.adherencePercentage,
    required this.schedule,
  });

  factory MedicationScheduleResponse.fromJson(Map<String, dynamic> json) {
    final list = (json['schedule'] as List<dynamic>? ?? [])
        .map((e) => MedicationItem.fromJson(e as Map<String, dynamic>))
        .toList();
    return MedicationScheduleResponse(
      today: json['today'] as String? ?? '',
      streakDays: json['streak_days'] as int? ?? 0,
      totalDoses: json['total_doses'] as int? ?? list.length,
      completedDoses: json['completed_doses'] as int? ?? 0,
      adherencePercentage: json['adherence_percentage'] as int? ?? 0,
      schedule: list,
    );
  }
}

