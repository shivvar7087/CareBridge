import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../models/medication.dart';
import '../services/copilot_service.dart';

class MedicationsScreen extends StatefulWidget {
  final VoidCallback? onUpdated;
  const MedicationsScreen({super.key, this.onUpdated});

  @override
  State<MedicationsScreen> createState() => _MedicationsScreenState();
}

class _MedicationsScreenState extends State<MedicationsScreen> {
  final _service = CopilotService();
  MedicationScheduleResponse? _medData;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMeds();
  }

  Future<void> _loadMeds() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final res = await _service.getMedications();
      if (mounted) {
        setState(() {
          _medData = res;
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

  void _showAddEditSheet([MedicationItem? existing]) {
    final messenger = ScaffoldMessenger.of(context);
    final nameCtrl = TextEditingController(text: existing?.name ?? '');
    final doseCtrl = TextEditingController(text: existing?.dosage ?? '');
    final timeCtrl = TextEditingController(text: existing?.timeLabel ?? '08:00 AM');
    final instCtrl = TextEditingController(text: existing?.instructions ?? '');
    String slot = existing?.timeSlot ?? 'Morning';

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
                      Text(
                        existing != null ? 'Edit Prescription' : 'Add Medication',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: nameCtrl,
                    decoration: const InputDecoration(labelText: 'Medicine Name (e.g. Atorvastatin)'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: doseCtrl,
                    decoration: const InputDecoration(labelText: 'Dosage (e.g. 20 mg, 1 tablet)'),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    initialValue: slot,
                    decoration: const InputDecoration(labelText: 'Time Slot'),
                    items: ['Morning', 'Afternoon', 'Evening', 'Bedtime']
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (val) => setSheetState(() => slot = val ?? 'Morning'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: timeCtrl,
                    decoration: const InputDecoration(labelText: 'Time (e.g. 08:00 AM)'),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: instCtrl,
                    decoration: const InputDecoration(labelText: 'Instructions (e.g. Take after meals with water)'),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () async {
                      if (nameCtrl.text.trim().isEmpty || doseCtrl.text.trim().isEmpty) return;
                      Navigator.pop(ctx);
                      try {
                        final payload = {
                          'name': nameCtrl.text.trim(),
                          'dosage': doseCtrl.text.trim(),
                          'time_slot': slot,
                          'time_label': timeCtrl.text.trim(),
                          'instructions': instCtrl.text.trim(),
                          'indication': '',
                        };
                        if (existing != null) {
                          await _service.updateMedication(existing.id, payload);
                        } else {
                          await _service.addMedication(payload);
                        }
                        _loadMeds();
                        widget.onUpdated?.call();
                      } catch (e) {
                        messenger.showSnackBar(
                          SnackBar(content: Text('Failed: $e'), backgroundColor: AppColors.danger),
                        );
                      }
                    },
                    child: Text(existing != null ? 'Save Changes' : 'Add to Schedule'),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Future<void> _deleteMed(MedicationItem med) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Prescription?'),
        content: Text('Are you sure you want to remove "${med.name}" from your daily schedule?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.danger),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _service.deleteMedication(med.id);
        _loadMeds();
        widget.onUpdated?.call();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error deleting: $e'), backgroundColor: AppColors.danger),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Prescription Schedule', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        actions: [
          IconButton(
            icon: const Icon(Icons.add, color: AppColors.primary),
            onPressed: () => _showAddEditSheet(),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
              : (_medData == null || _medData!.schedule.isEmpty)
                  ? const Center(child: Text('No prescribed medications found.'))
                  : RefreshIndicator(
                      color: AppColors.primary,
                      onRefresh: _loadMeds,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _medData!.schedule.length,
                        itemBuilder: (context, idx) {
                          final med = _medData!.schedule[idx];
                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              border: Border.all(color: AppColors.border),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 44,
                                  height: 44,
                                  decoration: BoxDecoration(
                                    color: AppColors.primaryBg,
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: const Icon(Icons.medication_rounded, color: AppColors.primary, size: 24),
                                ),
                                const SizedBox(width: 14),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Text(
                                            med.name,
                                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                          ),
                                          const SizedBox(width: 6),
                                          Text(
                                            med.dosage,
                                            style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        '${med.timeSlot} (${med.timeLabel})',
                                        style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600, fontSize: 12),
                                      ),
                                      if (med.instructions.isNotEmpty) ...[
                                        const SizedBox(height: 2),
                                        Text(
                                          med.instructions,
                                          style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.edit_outlined, size: 20, color: AppColors.textLight),
                                  onPressed: () => _showAddEditSheet(med),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete_outline, size: 20, color: AppColors.danger),
                                  onPressed: () => _deleteMed(med),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ),
    );
  }
}
