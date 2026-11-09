import 'package:flutter/material.dart';
import 'core/theme.dart';
import 'screens/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CareBridgeMobileApp());
}

class CareBridgeMobileApp extends StatelessWidget {
  const CareBridgeMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CareBridge',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const LoginScreen(),
    );
  }
}
