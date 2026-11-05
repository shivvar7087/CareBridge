import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/theme.dart';
import '../models/journey_task.dart';
import '../services/journey_service.dart';

class JourneyScreen extends StatefulWidget {
  const JourneyScreen({super.key});

  @override
  State<JourneyScreen> createState() => _JourneyScreenState();
}

class _JourneyScreenState extends State<JourneyScreen> {
  final _service = JourneyService();
  List<JourneyTask> _tasks = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadTimeline();
  }

  Future<void> _loadTimeline() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final tasks = await _service.getTimeline();
      if (mounted) {
        setState(() {
          _tasks = tasks;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _markComplete(JourneyTask task) async {
    try {
      await _service.updateTaskStatus(task.id, 'Completed');
      setState(() {
        task.status = 'Completed';
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Marked "${task.title}" as completed!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e'), backgroundColor: AppColors.danger),
        );
      }
    }
  }

  Map<String, List<JourneyTask>> _groupByDate(List<JourneyTask> tasks) {
    final Map<String, List<JourneyTask>> map = {};
    for (final t in tasks) {
      final key = t.dueDate ?? 'undated';
      map.putIfAbsent(key, () => []).add(t);
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: AppColors.primary));
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!, style: const TextStyle(color: AppColors.danger)),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: _loadTimeline, child: const Text('Retry')),
          ],
        ),
      );
    }

    final grouped = _groupByDate(_tasks);
    final todayStr = DateFormat('yyyy-MM-dd').format(DateTime.now());

    return Scaffold(
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: _loadTimeline,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Screen Header
            const Text(
              'CARE PLAN TIMELINE',
              style: TextStyle(color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.6),
            ),
            const SizedBox(height: 4),
            const Text(
              'My Healthcare Journey',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textDark),
            ),
            const SizedBox(height: 4),
            const Text(
              'Chronological milestones of clinician instructions and recovery tasks.',
              style: TextStyle(color: AppColors.textMuted, fontSize: 13),
            ),
            const SizedBox(height: 20),

            if (grouped.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Text('No healthcare journey milestones recorded.'),
                ),
              )
            else
              ...grouped.entries.map((entry) {
                final dateKey = entry.key;
                final dayTasks = entry.value;
                final isToday = dateKey == todayStr;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Date Header
                    Container(
                      margin: const EdgeInsets.symmetric(vertical: 10),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: isToday ? AppColors.primaryBg : AppColors.background,
                        border: Border.all(color: isToday ? AppColors.primary : AppColors.border),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (isToday) ...[
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.primary,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text('TODAY', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                            ),
                            const SizedBox(width: 8),
                          ],
                          Text(
                            dateKey == 'undated' ? 'DATE TO BE CONFIRMED' : dateKey,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 12.5,
                              color: isToday ? AppColors.primaryDark : AppColors.textDark,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Tasks on this date
                    ...dayTasks.map((task) => Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(
                              color: task.isToday && !task.isCompleted
                                  ? AppColors.primary
                                  : task.isOverdue
                                      ? AppColors.danger
                                      : AppColors.border,
                              width: (task.isToday && !task.isCompleted) || task.isOverdue ? 1.5 : 1,
                            ),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(14),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Icon(
                                      task.category == 'Appointment'
                                          ? Icons.calendar_today_rounded
                                          : task.category == 'Diagnostic Test'
                                              ? Icons.biotech_rounded
                                              : task.category == 'Hospital Discharge'
                                                  ? Icons.local_hospital_outlined
                                                  : Icons.task_alt_rounded,
                                      color: AppColors.primary,
                                      size: 20,
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            task.title,
                                            style: TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 15,
                                              decoration: task.isCompleted ? TextDecoration.lineThrough : null,
                                            ),
                                          ),
                                          const SizedBox(height: 2),
                                          Text(
                                            task.description.isNotEmpty ? task.description : 'No additional details.',
                                            style: const TextStyle(color: AppColors.textMuted, fontSize: 12.5),
                                          ),
                                        ],
                                      ),
                                    ),
                                    _buildStatusChip(task.status),
                                  ],
                                ),
                                const SizedBox(height: 10),
                                const Divider(height: 1, color: AppColors.border),
                                const SizedBox(height: 8),

                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      task.category,
                                      style: const TextStyle(color: AppColors.textLight, fontSize: 11, fontWeight: FontWeight.bold),
                                    ),
                                    if (!task.isCompleted)
                                      TextButton.icon(
                                        onPressed: () => _markComplete(task),
                                        icon: const Icon(Icons.check, size: 16),
                                        label: const Text('Mark Done', style: TextStyle(fontSize: 12)),
                                        style: TextButton.styleFrom(
                                          foregroundColor: AppColors.primary,
                                          visualDensity: VisualDensity.compact,
                                        ),
                                      ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        )),
                  ],
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color bg = const Color(0xFFF1F5F9);
    Color fg = const Color(0xFF475569);

    if (status == 'Completed') {
      bg = AppColors.successBg;
      fg = AppColors.success;
    } else if (status == 'Overdue') {
      bg = AppColors.dangerBg;
      fg = AppColors.danger;
    } else if (status == 'Scheduled') {
      bg = AppColors.infoBg;
      fg = AppColors.info;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(6)),
      child: Text(status, style: TextStyle(color: fg, fontSize: 11, fontWeight: FontWeight.bold)),
    );
  }
}
