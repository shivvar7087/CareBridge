import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../models/medication.dart';
import '../services/dashboard_service.dart';
import '../services/copilot_service.dart';
import 'emergency_card_screen.dart';
import 'medications_screen.dart';

class DashboardScreen extends StatefulWidget {
  final Function(int) onTabChange;
  const DashboardScreen({super.key, required this.onTabChange});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _dashService = DashboardService();
  final _copilotService = CopilotService();

  Map<String, dynamic>? _dashData;
  MedicationScheduleResponse? _medData;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final dashRes = await _dashService.getDashboard();
      final medRes = await _copilotService.getMedications();
      if (mounted) {
        setState(() {
          _dashData = dashRes;
          _medData = medRes;
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

  String _getGreeting(String? fullName) {
    final hour = DateTime.now().hour;
    final first = (fullName != null && fullName.isNotEmpty) ? fullName.split(' ').first : 'there';
    if (hour < 12) return 'Good morning, $first 🌅';
    if (hour < 17) return 'Good afternoon, $first ☀️';
    return 'Good evening, $first 🌙';
  }

  Future<void> _toggleMedication(MedicationItem med) async {
    final nextStatus = !med.taken;
    setState(() {
      med.taken = nextStatus;
    });
    try {
      await _copilotService.logMedication(med.id, nextStatus);
    } catch (_) {
      // Revert if error
      setState(() {
        med.taken = !nextStatus;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading && _dashData == null) {
      return const Center(child: CircularProgressIndicator(color: AppColors.primary));
    }

    if (_error != null && _dashData == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.cloud_off_rounded, size: 48, color: AppColors.textLight),
              const SizedBox(height: 12),
              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: AppColors.danger)),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Retry Connection'),
              ),
            ],
          ),
        ),
      );
    }

    final summary = _dashData?['summary'] as Map<String, dynamic>? ?? {};
    final patient = _dashData?['patient'] as Map<String, dynamic>? ?? {};
    final appts = (_dashData?['upcoming_appointments'] as List<dynamic>? ?? []);
    final totalTasks = summary['total_tasks'] ?? 0;
    final completedTasks = summary['completed_tasks'] ?? 0;
    final pendingTasks = summary['pending_tasks'] ?? 0;
    final overdueTasks = summary['overdue_tasks'] ?? 0;

    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Greeting & Welcome Banner
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0F2537), Color(0xFF1E3A53)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF0F2537).withValues(alpha: 0.2),
                  blurRadius: 14,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'YOUR CARE, COORDINATED',
                      style: TextStyle(
                        color: AppColors.primaryLight,
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                      ),
                    ),
                    if (patient['is_demo'] == true)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text(
                          'DEMO MODE',
                          style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  _getGreeting(patient['name']),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Here is your recovery and care roadmap for today.',
                  style: TextStyle(color: Color(0xFFCBD5E1), fontSize: 13),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Quick Action Shortcuts Bar
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildQuickAction(
                  icon: Icons.shield_outlined,
                  label: 'Emergency Card',
                  color: AppColors.danger,
                  bg: AppColors.dangerBg,
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const EmergencyCardScreen()),
                    );
                  },
                ),
                const SizedBox(width: 8),
                _buildQuickAction(
                  icon: Icons.chat_bubble_outline_rounded,
                  label: 'Ask AI Copilot',
                  color: AppColors.primary,
                  bg: AppColors.primaryBg,
                  onTap: () => widget.onTabChange(4),
                ),
                const SizedBox(width: 8),
                _buildQuickAction(
                  icon: Icons.timeline_rounded,
                  label: 'Journey Steps',
                  color: AppColors.info,
                  bg: AppColors.infoBg,
                  onTap: () => widget.onTabChange(1),
                ),
                const SizedBox(width: 8),
                _buildQuickAction(
                  icon: Icons.medication_outlined,
                  label: 'Prescriptions',
                  color: AppColors.warning,
                  bg: AppColors.warningBg,
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => MedicationsScreen(onUpdated: _loadData),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Stats 2x2 Grid
          Row(
            children: [
              Expanded(child: _buildStatCard('Total Tasks', '$totalTasks', Icons.format_list_bulleted_rounded, AppColors.info)),
              const SizedBox(width: 10),
              Expanded(child: _buildStatCard('Completed', '$completedTasks', Icons.check_circle_outline_rounded, AppColors.success)),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(child: _buildStatCard('In Progress', '$pendingTasks', Icons.hourglass_top_rounded, AppColors.warning)),
              const SizedBox(width: 10),
              Expanded(child: _buildStatCard('Overdue', '$overdueTasks', Icons.warning_amber_rounded, AppColors.danger)),
            ],
          ),
          const SizedBox(height: 18),

          // Today's Medication Tracker Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text('DAILY PRESCRIPTIONS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary)),
                          Text('Today’s Medication Tracker', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.textDark)),
                        ],
                      ),
                      if (_medData?.streakDays != null && _medData!.streakDays > 0)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFFF7ED),
                            border: Border.all(color: const Color(0xFFFFEDD5)),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              const Text('🔥', style: TextStyle(fontSize: 14)),
                              const SizedBox(width: 4),
                              Text(
                                '${_medData!.streakDays}-Day Streak',
                                style: const TextStyle(color: Color(0xFFEA580C), fontWeight: FontWeight.bold, fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  if (_medData != null && _medData!.schedule.isNotEmpty) ...[
                    // Adherence Meter
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Doses Taken: ${_medData!.completedDoses} of ${_medData!.totalDoses}',
                                style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w600, color: AppColors.textDark),
                              ),
                              Text(
                                '${_medData!.adherencePercentage}%',
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.primary),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: _medData!.totalDoses > 0 ? _medData!.completedDoses / _medData!.totalDoses : 0,
                              backgroundColor: const Color(0xFFE2E8F0),
                              valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                              minHeight: 6,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Pills list
                    ..._medData!.schedule.map((med) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: InkWell(
                            onTap: () => _toggleMedication(med),
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                              decoration: BoxDecoration(
                                color: med.taken ? AppColors.primaryBg : Colors.white,
                                border: Border.all(
                                  color: med.taken ? const Color(0xFF99F6E4) : AppColors.border,
                                ),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    med.taken ? Icons.check_box_rounded : Icons.check_box_outline_blank_rounded,
                                    color: med.taken ? AppColors.primary : AppColors.textLight,
                                    size: 24,
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          children: [
                                            Text(
                                              med.name,
                                              style: TextStyle(
                                                fontSize: 14.5,
                                                fontWeight: FontWeight.bold,
                                                color: med.taken ? AppColors.primaryDark : AppColors.textDark,
                                                decoration: med.taken ? TextDecoration.lineThrough : null,
                                              ),
                                            ),
                                            const SizedBox(width: 6),
                                            Text(med.dosage, style: const TextStyle(fontSize: 12.5, color: AppColors.textMuted)),
                                          ],
                                        ),
                                        Text(
                                          '${med.timeSlot} (${med.timeLabel}) · ${med.instructions}',
                                          style: const TextStyle(fontSize: 11.5, color: AppColors.textMuted),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        )),
                  ] else ...[
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Text('No active prescribed medications.', style: TextStyle(color: AppColors.textMuted)),
                    ),
                  ],

                  const SizedBox(height: 8),
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton.icon(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => MedicationsScreen(onUpdated: _loadData)),
                        );
                      },
                      icon: const Icon(Icons.settings_outlined, size: 16),
                      label: const Text('Manage Schedule'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Upcoming Appointments
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('CALENDAR MILESTONES', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary)),
                  const Text('Upcoming Appointments', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppColors.textDark)),
                  const SizedBox(height: 12),

                  if (appts.isNotEmpty) ...[
                    ...appts.map((appt) => Container(
                          margin: const EdgeInsets.only(bottom: 10),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppColors.background,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: AppColors.border),
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
                                child: const Icon(Icons.calendar_month_rounded, color: AppColors.primary, size: 22),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      appt['title'] ?? 'Appointment',
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                    ),
                                    Text(
                                      appt['due_date'] ?? 'Date to be confirmed',
                                      style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        )),
                  ] else ...[
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8),
                      child: Text('No upcoming appointments scheduled.', style: TextStyle(color: AppColors.textMuted)),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8),
            alignment: Alignment.center,
            child: Column(
              children: const [
                Text(
                  'Team ByteCoders · IIMT Engineering College, Meerut',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textDark,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Smart Automation · Post Discharge Healthcare Coordination System',
                  style: TextStyle(fontSize: 9.5, color: AppColors.textMuted),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String label,
    required Color color,
    required Color bg,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: bg,
          border: Border.all(color: color.withValues(alpha: 0.2)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(icon, size: 18, color: color),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12.5),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
              Icon(icon, color: color, size: 20),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: color),
          ),
        ],
      ),
    );
  }
}
