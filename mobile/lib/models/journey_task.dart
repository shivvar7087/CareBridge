import 'package:intl/intl.dart';

class JourneyTask {
  final int id;
  final int patientId;
  final String title;
  final String description;
  final String category;
  String status;
  final String? dueDate;
  final bool needsVerification;
  final int? assignedToId;

  JourneyTask({
    required this.id,
    required this.patientId,
    required this.title,
    required this.description,
    required this.category,
    required this.status,
    this.dueDate,
    this.needsVerification = false,
    this.assignedToId,
  });

  factory JourneyTask.fromJson(Map<String, dynamic> json) {
    return JourneyTask(
      id: json['id'] as int,
      patientId: json['patient_id'] as int,
      title: json['title'] as String? ?? 'Untitled Task',
      description: json['description'] as String? ?? '',
      category: json['category'] as String? ?? 'Other',
      status: json['status'] as String? ?? 'Pending',
      dueDate: json['due_date'] as String?,
      needsVerification: json['needs_clinician_verification'] as bool? ?? false,
      assignedToId: json['assigned_to_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'category': category,
      'status': status,
      'due_date': dueDate,
      'assigned_to_id': assignedToId,
    };
  }

  bool get isCompleted => status == 'Completed';

  bool get isToday {
    if (dueDate == null) return false;
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    return dueDate == today;
  }

  bool get isOverdue {
    if (dueDate == null || isCompleted) return false;
    final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
    return dueDate!.compareTo(today) < 0;
  }

  String get formattedDate {
    if (dueDate == null) return 'No due date';
    try {
      final parsed = DateTime.parse(dueDate!);
      return DateFormat('d MMM yyyy').format(parsed);
    } catch (_) {
      return dueDate!;
    }
  }
}
