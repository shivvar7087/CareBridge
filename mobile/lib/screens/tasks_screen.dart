import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../core/theme.dart';
import '../models/journey_task.dart';
import '../services/journey_service.dart';

class TasksScreen extends StatefulWidget {
  const TasksScreen({super.key});

  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {
  final _service = JourneyService();
  List<JourneyTask> _tasks = [];
  String _selectedFilter = 'All';
  bool _loading = true;
  String? _error;

  final List<String> _filters = ['All', 'Pending', 'In Progress', 'Scheduled', 'Overdue', 'Completed'];

  @override
  void initState() {
    super.initState();
    _loadTasks();
  }

  Future<void> _loadTasks() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final tasks = await _service.getTasks(_selectedFilter);
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
          SnackBar(content: Text('Completed "${task.title}"')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.danger),
        );
      }
    }
  }

  void _showAddTaskSheet() {
    final messenger = ScaffoldMessenger.of(context);
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    String category = 'Other';
    String? dueDate;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setSheetState) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(context).viewInsets.bottom + 24,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Add Journey Task', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: titleCtrl,
                    decoration: const InputDecoration(labelText: 'Task Title (e.g. Upload lab report)'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: descCtrl,
                    maxLines: 2,
                    decoration: const InputDecoration(labelText: 'Description / Instructions'),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    initialValue: category,
                    decoration: const InputDecoration(labelText: 'Category'),
                    items: ['Other', 'Appointment', 'Diagnostic Test', 'Report Collection', 'Hospital Discharge', 'Follow-up']
                        .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                        .toList(),
                    onChanged: (val) => setSheetState(() => category = val ?? 'Other'),
                  ),
                  const SizedBox(height: 12),
                  ListTile(
                    title: Text(dueDate != null ? 'Due: $dueDate' : 'Select Due Date'),
                    trailing: const Icon(Icons.calendar_today, size: 20),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: const BorderSide(color: AppColors.border),
                    ),
                    onTap: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: DateTime.now(),
                        firstDate: DateTime.now().subtract(const Duration(days: 30)),
                        lastDate: DateTime.now().add(const Duration(days: 365)),
                      );
                      if (picked != null) {
                        setSheetState(() {
                          dueDate = DateFormat('yyyy-MM-dd').format(picked);
                        });
                      }
                    },
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () async {
                      if (titleCtrl.text.trim().isEmpty) return;
                      Navigator.pop(ctx);
                      try {
                        await _service.createTask({
                          'title': titleCtrl.text.trim(),
                          'description': descCtrl.text.trim(),
                          'category': category,
                          'due_date': dueDate,
                          'status': 'Pending',
                        });
                        _loadTasks();
                        messenger.showSnackBar(
                          const SnackBar(content: Text('Task added to journey!')),
                        );
                      } catch (e) {
                        messenger.showSnackBar(
                          SnackBar(content: Text('Failed: $e'), backgroundColor: AppColors.danger),
                        );
                      }
                    },
                    child: const Text('Add to Care Journey'),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddTaskSheet,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: const Text('New Task'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Filter Bar
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: _filters.map((f) {
                  final isSelected = _selectedFilter == f;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: FilterChip(
                      label: Text(f),
                      selected: isSelected,
                      selectedColor: AppColors.primaryBg,
                      checkmarkColor: AppColors.primary,
                      labelStyle: TextStyle(
                        color: isSelected ? AppColors.primaryDark : AppColors.textDark,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        fontSize: 12.5,
                      ),
                      onSelected: (val) {
                        setState(() => _selectedFilter = f);
                        _loadTasks();
                      },
                    ),
                  );
                }).toList(),
              ),
            ),

            // Tasks List
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
                  : _error != null
                      ? Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
                      : _tasks.isEmpty
                          ? const Center(child: Text('No tasks matching this filter.'))
                          : RefreshIndicator(
                              color: AppColors.primary,
                              onRefresh: _loadTasks,
                              child: ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                itemCount: _tasks.length,
                                itemBuilder: (context, idx) {
                                  final task = _tasks[idx];
                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 10),
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
                                    child: ListTile(
                                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                      leading: IconButton(
                                        icon: Icon(
                                          task.isCompleted ? Icons.check_circle_rounded : Icons.radio_button_unchecked,
                                          color: task.isCompleted ? AppColors.success : AppColors.textLight,
                                          size: 26,
                                        ),
                                        onPressed: task.isCompleted ? null : () => _markComplete(task),
                                      ),
                                      title: Row(
                                        children: [
                                          Expanded(
                                            child: Text(
                                              task.title,
                                              style: TextStyle(
                                                fontWeight: FontWeight.bold,
                                                fontSize: 15,
                                                decoration: task.isCompleted ? TextDecoration.lineThrough : null,
                                              ),
                                            ),
                                          ),
                                          if (task.isToday && !task.isCompleted)
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: AppColors.primary,
                                                borderRadius: BorderRadius.circular(4),
                                              ),
                                              child: const Text('TODAY', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                                            )
                                          else if (task.isOverdue)
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: AppColors.dangerBg,
                                                border: Border.all(color: AppColors.dangerBorder),
                                                borderRadius: BorderRadius.circular(4),
                                              ),
                                              child: const Text('OVERDUE', style: TextStyle(color: AppColors.danger, fontSize: 10, fontWeight: FontWeight.bold)),
                                            ),
                                        ],
                                      ),
                                      subtitle: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          if (task.description.isNotEmpty) ...[
                                            const SizedBox(height: 4),
                                            Text(task.description, style: const TextStyle(fontSize: 12.5, color: AppColors.textMuted)),
                                          ],
                                          const SizedBox(height: 6),
                                          Row(
                                            children: [
                                              const Icon(Icons.calendar_today, size: 12, color: AppColors.textLight),
                                              const SizedBox(width: 4),
                                              Text(task.formattedDate, style: const TextStyle(fontSize: 11.5, color: AppColors.textMuted)),
                                              const SizedBox(width: 8),
                                              Text('·  ${task.category}', style: const TextStyle(fontSize: 11.5, color: AppColors.textLight)),
                                            ],
                                          ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              ),
                            ),
            ),
          ],
        ),
      ),
    );
  }
}
