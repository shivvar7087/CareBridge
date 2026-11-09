import 'package:flutter/material.dart';

import '../core/theme.dart';
import '../core/api_client.dart';
import 'emergency_card_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _client = ApiClient();
  final _phoneController = TextEditingController();
  final _hospitalController = TextEditingController();
  final _emergencyNameController = TextEditingController();
  final _emergencyPhoneController = TextEditingController();

  String _selectedBloodGroup = 'B+ Positive';
  String _selectedLanguage = 'English';
  bool _notifyMorning = true;
  bool _notifyEvening = true;
  bool _notifyAppointments = true;
  bool _organDonor = true;

  bool _loading = true;
  bool _saving = false;
  String? _message;

  final List<String> _bloodGroups = [
    'A+',
    'A-',
    'B+',
    'B-',
    'O+',
    'O-',
    'AB+',
    'AB-',
    'B+ Positive',
  ];

  final List<String> _languages = [
    'English',
    'Hindi (हिंदी)',
    'Bengali (বাংলা)',
    'Tamil (தமிழ்)',
    'Telugu (తెలుగు)',
    'Marathi (मराठी)',
  ];

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final res = await _client.get('/patients/me') as Map<String, dynamic>;
      if (mounted) {
        setState(() {
          _phoneController.text = res['phone'] as String? ?? '';
          _hospitalController.text = res['hospital_name'] as String? ?? '';
          _selectedLanguage = res['preferred_language'] as String? ?? 'English';
          if (res['blood_group'] != null) {
            _selectedBloodGroup = res['blood_group'] as String;
          }
          if (res['emergency_contact_name'] != null) {
            _emergencyNameController.text =
                res['emergency_contact_name'] as String;
          }
          if (res['emergency_contact_phone'] != null) {
            _emergencyPhoneController.text =
                res['emergency_contact_phone'] as String;
          }
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _saveSettings() async {
    setState(() {
      _saving = true;
      _message = null;
    });

    try {
      await _client.put('/patients/me', {
        'phone': _phoneController.text.trim().isEmpty
            ? null
            : _phoneController.text.trim(),
        'hospital_name': _hospitalController.text.trim().isEmpty
            ? null
            : _hospitalController.text.trim(),
        'preferred_language': _selectedLanguage.split(' ')[0],
        'blood_group': _selectedBloodGroup,
        'emergency_contact_name': _emergencyNameController.text.trim().isEmpty
            ? null
            : _emergencyNameController.text.trim(),
        'emergency_contact_phone': _emergencyPhoneController.text.trim().isEmpty
            ? null
            : _emergencyPhoneController.text.trim(),
      });

      if (mounted) {
        setState(() {
          _saving = false;
          _message = 'Settings saved successfully!';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Settings and Emergency ICE profile saved!'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving settings: $e'),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Settings & Emergency ID',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_message != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FDF4),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFBBF7D0)),
                    ),
                    child: Text(
                      _message!,
                      style: const TextStyle(
                        color: Color(0xFF166534),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),

                // Section 1: Emergency ICE ID
                _buildSectionHeader(
                  '🚨 Emergency ICE Medical ID',
                  'Critical triage data for paramedics (< 5s)',
                ),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Blood Group:',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: _bloodGroups.map((bg) {
                            final selected = _selectedBloodGroup == bg;
                            return ChoiceChip(
                              label: Text(
                                bg,
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                  color: selected
                                      ? Colors.white
                                      : AppColors.textDark,
                                ),
                              ),
                              selected: selected,
                              selectedColor: AppColors.danger,
                              backgroundColor: const Color(0xFFF8FAFC),
                              onSelected: (_) =>
                                  setState(() => _selectedBloodGroup = bg),
                            );
                          }).toList(),
                        ),
                        const SizedBox(height: 14),

                        TextField(
                          controller: _emergencyNameController,
                          decoration: const InputDecoration(
                            labelText: 'Emergency Contact Person',
                            hintText: 'e.g. Priya Sharma (Caregiver)',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                        ),
                        const SizedBox(height: 10),

                        TextField(
                          controller: _emergencyPhoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                            labelText: 'Emergency Contact Phone',
                            hintText: '+91 98765 43210',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                        ),
                        const SizedBox(height: 10),

                        SwitchListTile(
                          contentPadding: EdgeInsets.zero,
                          title: const Text(
                            'Registered Organ Donor',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          subtitle: const Text(
                            'Displays donor status on paramedic scan',
                            style: TextStyle(
                              fontSize: 11.5,
                              color: AppColors.textMuted,
                            ),
                          ),
                          value: _organDonor,
                          activeThumbColor: AppColors.danger,
                          onChanged: (val) => setState(() => _organDonor = val),
                        ),

                        OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: AppColors.danger,
                            side: const BorderSide(color: AppColors.danger),
                          ),
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const EmergencyCardScreen(),
                              ),
                            );
                          },
                          icon: const Icon(Icons.qr_code_2, size: 18),
                          label: const Text(
                            'Preview Paramedic QR Passport (< 5s)',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 18),

                // Section 2: Clinical & Regional
                _buildSectionHeader(
                  '👤 Patient Profile & Hospital',
                  'Contact details and attending facility',
                ),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        TextField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                            labelText: 'Your Contact Phone',
                            hintText: '+91 98100 23456',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                        ),
                        const SizedBox(height: 12),

                        TextField(
                          controller: _hospitalController,
                          decoration: const InputDecoration(
                            labelText: 'Attending Hospital / Clinic',
                            hintText: 'Harborview Medical Centre',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                        ),
                        const SizedBox(height: 12),

                        DropdownButtonFormField<String>(
                          initialValue: _languages.contains(_selectedLanguage)
                              ? _selectedLanguage
                              : _languages.first,
                          decoration: const InputDecoration(
                            labelText: 'Preferred Language',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: _languages
                              .map(
                                (l) => DropdownMenuItem(
                                  value: l,
                                  child: Text(
                                    l,
                                    style: const TextStyle(fontSize: 13),
                                  ),
                                ),
                              )
                              .toList(),
                          onChanged: (val) {
                            if (val != null)
                              setState(() => _selectedLanguage = val);
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 18),

                // Section 3: Notification Schedules
                _buildSectionHeader(
                  '🔔 Reminders & Notification Schedules',
                  'Automated alarms for medications and appointments',
                ),
                Card(
                  child: Column(
                    children: [
                      SwitchListTile(
                        title: const Text(
                          'Morning Medication Alarm (08:00 AM)',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        subtitle: const Text(
                          'Aspirin, Metformin reminders',
                          style: TextStyle(
                            fontSize: 11.5,
                            color: AppColors.textMuted,
                          ),
                        ),
                        value: _notifyMorning,
                        onChanged: (v) => setState(() => _notifyMorning = v),
                      ),
                      const Divider(height: 1),
                      SwitchListTile(
                        title: const Text(
                          'Bedtime Medication Reminder (08:00 PM)',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        subtitle: const Text(
                          'Atorvastatin & evening doses',
                          style: TextStyle(
                            fontSize: 11.5,
                            color: AppColors.textMuted,
                          ),
                        ),
                        value: _notifyEvening,
                        onChanged: (v) => setState(() => _notifyEvening = v),
                      ),
                      const Divider(height: 1),
                      SwitchListTile(
                        title: const Text(
                          '24-Hour Advance Appointment Alerts',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        subtitle: const Text(
                          'Reminders for clinic milestones',
                          style: TextStyle(
                            fontSize: 11.5,
                            color: AppColors.textMuted,
                          ),
                        ),
                        value: _notifyAppointments,
                        onChanged: (v) =>
                            setState(() => _notifyAppointments = v),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),

                // Save Button
                ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  onPressed: _saving ? null : _saveSettings,
                  icon: const Icon(Icons.save_rounded, size: 20),
                  label: Text(
                    _saving ? 'Saving Settings…' : 'Save All Preferences',
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.w800,
              fontSize: 15,
              color: AppColors.textDark,
            ),
          ),
          Text(
            subtitle,
            style: const TextStyle(fontSize: 11.5, color: AppColors.textMuted),
          ),
        ],
      ),
    );
  }
}
