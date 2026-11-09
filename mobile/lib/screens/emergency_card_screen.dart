import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../models/emergency_card.dart';
import '../services/copilot_service.dart';

class EmergencyCardScreen extends StatefulWidget {
  const EmergencyCardScreen({super.key});

  @override
  State<EmergencyCardScreen> createState() => _EmergencyCardScreenState();
}

class _EmergencyCardScreenState extends State<EmergencyCardScreen> {
  final _service = CopilotService();
  EmergencyCardData? _data;
  bool _loading = true;
  String? _error;
  bool _sosSent = false;
  bool _sendingSos = false;

  @override
  void initState() {
    super.initState();
    _loadCard();
  }

  Future<void> _loadCard() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final res = await _service.getEmergencyCard();
      if (mounted) {
        setState(() {
          _data = res;
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

  Future<void> _broadcastSos() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('🚨 Broadcast Emergency SOS?'),
        content: const Text(
          'This will send an immediate, high-priority emergency notification to all linked family members and caregivers.',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.danger),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Send Alert Now'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      setState(() => _sendingSos = true);
      try {
        await _service.sendEmergencySos();
        setState(() {
          _sosSent = true;
          _sendingSos = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Emergency SOS sent to all active caregivers!'),
              backgroundColor: AppColors.danger,
            ),
          );
        }
      } catch (e) {
        setState(() => _sendingSos = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed: $e'), backgroundColor: AppColors.danger),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency Medical Card', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: AppColors.danger))
          : _error != null
              ? Center(child: Text(_error!, style: const TextStyle(color: AppColors.danger)))
              : _data == null
                  ? const Center(child: Text('No emergency data available.'))
                  : ListView(
                      padding: const EdgeInsets.all(16),
                      children: [
                        // Urgent SOS Broadcast Bar
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppColors.dangerBg,
                            border: Border.all(color: AppColors.dangerBorder),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Row(
                                children: const [
                                  Icon(Icons.warning_amber_rounded, color: AppColors.danger, size: 24),
                                  SizedBox(width: 8),
                                  Text(
                                    'IMMEDIATE TRIAGE & HELP',
                                    style: TextStyle(color: AppColors.danger, fontWeight: FontWeight.bold, fontSize: 12),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              const Text(
                                'Tap below to instantly alert all connected caregivers with an urgent medical assistance notification.',
                                style: TextStyle(color: Color(0xFF881337), fontSize: 12.5),
                              ),
                              const SizedBox(height: 12),
                              ElevatedButton.icon(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: _sosSent ? AppColors.success : AppColors.danger,
                                  foregroundColor: Colors.white,
                                ),
                                onPressed: _sendingSos ? null : _broadcastSos,
                                icon: Icon(_sosSent ? Icons.check : Icons.phone_forwarded, size: 18),
                                label: Text(_sosSent ? 'Caregivers Alerted' : _sendingSos ? 'Sending…' : 'Broadcast Emergency SOS'),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Patient Identity Card
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: AppColors.border),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 50,
                                height: 50,
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF1F5F9),
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: const Icon(Icons.person, color: AppColors.textDark, size: 28),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _data!.fullName,
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                                    ),
                                    Text(
                                      'DOB: ${_data!.dateOfBirth} · ${_data!.phone}',
                                      style: const TextStyle(color: AppColors.textMuted, fontSize: 12.5),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: AppColors.dangerBg,
                                  border: Border.all(color: AppColors.danger, width: 1.5),
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: Column(
                                  children: [
                                    const Text('BLOOD', style: TextStyle(color: AppColors.danger, fontSize: 9, fontWeight: FontWeight.bold)),
                                    Text(_data!.bloodGroup, style: const TextStyle(color: AppColors.danger, fontWeight: FontWeight.w800, fontSize: 13)),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),

                        // Paramedic Fast-Scan QR Passport Card
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: const Color(0xFFCBD5E1)),
                            borderRadius: BorderRadius.circular(16),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: 0.02),
                                blurRadius: 4,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Row(
                            children: [
                              ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Image.network(
                                  'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https%3A%2F%2Fcarebridge-1-9b9i.onrender.com%2Fice%2F1',
                                  width: 80,
                                  height: 80,
                                  errorBuilder: (context, error, stackTrace) => Container(
                                    width: 80,
                                    height: 80,
                                    color: const Color(0xFFF1F5F9),
                                    child: const Icon(Icons.qr_code_2, size: 48, color: AppColors.textDark),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: const [
                                    Text(
                                      '⚡ FAST-TRIAGE QR (< 5s)',
                                      style: TextStyle(
                                        color: AppColors.danger,
                                        fontWeight: FontWeight.w800,
                                        fontSize: 12,
                                        letterSpacing: 0.5,
                                      ),
                                    ),
                                    SizedBox(height: 4),
                                    Text(
                                      'First responders can scan this code with any camera for instant triage, blood group, allergies & hospital helpline.',
                                      style: TextStyle(color: AppColors.textMuted, fontSize: 11.5, height: 1.3),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),

                        // Known Allergies Box
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: const Color(0xFFFECACA)),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: const [
                                  Icon(Icons.error_outline, color: AppColors.danger, size: 18),
                                  SizedBox(width: 6),
                                  Text('Known Allergies', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.danger, fontSize: 14)),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                runSpacing: 6,
                                children: _data!.allergies.map((allergy) => Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: AppColors.dangerBg,
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(allergy, style: const TextStyle(color: Color(0xFF991B1B), fontSize: 12.5, fontWeight: FontWeight.w600)),
                                    )).toList(),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),

                        // Chronic Conditions
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: const Color(0xFFFED7AA)),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: const [
                                  Icon(Icons.favorite_outline, color: Color(0xFFEA580C), size: 18),
                                  SizedBox(width: 6),
                                  Text('Chronic Conditions', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFEA580C), fontSize: 14)),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                runSpacing: 6,
                                children: _data!.chronicConditions.map((cond) => Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFFFF7ED),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Text(cond, style: const TextStyle(color: Color(0xFF9A3412), fontSize: 12.5, fontWeight: FontWeight.w600)),
                                    )).toList(),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),

                        // Hospital & Doctor
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: AppColors.border),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Attending Hospital & Doctor', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                              const SizedBox(height: 6),
                              Text(_data!.hospitalName, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                              Text('Physician: ${_data!.primaryPhysician}', style: const TextStyle(color: AppColors.textMuted, fontSize: 13)),
                              if (_data!.hospitalHelpline.isNotEmpty) ...[
                                const SizedBox(height: 6),
                                Text('Helpline: ${_data!.hospitalHelpline}', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 13)),
                              ],
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),

                        // Caregiver Emergency Contacts
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: AppColors.border),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Connected Family Caregivers', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                              const SizedBox(height: 10),
                              ..._data!.caregivers.map((cg) => Padding(
                                    padding: const EdgeInsets.only(bottom: 8),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Text(cg.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                                            Text('${cg.relation} · ${cg.phone}', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                                          ],
                                        ),
                                        const Icon(Icons.phone, color: AppColors.primary, size: 20),
                                      ],
                                    ),
                                  )),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          alignment: Alignment.center,
                          child: const Text(
                            'CareBridge Emergency ICE · ByteCoders\nIIMT Engineering College, Meerut',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: AppColors.textMuted, fontSize: 11, fontWeight: FontWeight.w500),
                          ),
                        ),
                        const SizedBox(height: 24),
                      ],
                    ),
    );
  }
}

