import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../core/api_client.dart';
import 'dashboard_screen.dart';
import 'journey_screen.dart';
import 'tasks_screen.dart';
import 'medications_screen.dart';
import 'copilot_chat_screen.dart';
import 'emergency_card_screen.dart';
import 'settings_screen.dart';
import 'login_screen.dart';

class HomeNavigationScreen extends StatefulWidget {
  const HomeNavigationScreen({super.key});

  @override
  State<HomeNavigationScreen> createState() => _HomeNavigationScreenState();
}

class _HomeNavigationScreenState extends State<HomeNavigationScreen> {
  int _currentIndex = 0;
  final _client = ApiClient();

  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    _pages = [
      DashboardScreen(onTabChange: (idx) => setState(() => _currentIndex = idx)),
      const JourneyScreen(),
      const TasksScreen(),
      const MedicationsScreen(),
      const CopilotChatScreen(),
    ];
  }

  void _signOut() {
    _client.clearAuth();
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text(
              'carebridge',
              style: TextStyle(fontWeight: FontWeight.w800, fontSize: 19, letterSpacing: -0.5),
            ),
            const Text(
              ' AI',
              style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w800, fontSize: 19),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.shield_outlined, color: AppColors.danger),
            tooltip: 'Emergency Medical ID',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const EmergencyCardScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: AppColors.textDark),
            tooltip: 'Settings & Emergency ID',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded, color: AppColors.textLight, size: 20),
            tooltip: 'Sign Out',
            onPressed: _signOut,
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        backgroundColor: Colors.white,
        elevation: 2,
        indicatorColor: AppColors.primaryBg,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard_rounded, color: AppColors.primary),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.timeline_outlined),
            selectedIcon: Icon(Icons.timeline_rounded, color: AppColors.primary),
            label: 'Journey',
          ),
          NavigationDestination(
            icon: Icon(Icons.check_box_outlined),
            selectedIcon: Icon(Icons.check_box_rounded, color: AppColors.primary),
            label: 'Tasks',
          ),
          NavigationDestination(
            icon: Icon(Icons.medication_outlined),
            selectedIcon: Icon(Icons.medication_rounded, color: AppColors.primary),
            label: 'Pills',
          ),
          NavigationDestination(
            icon: Icon(Icons.auto_awesome_outlined),
            selectedIcon: Icon(Icons.auto_awesome, color: AppColors.primary),
            label: 'Copilot',
          ),
        ],
      ),
    );
  }
}

