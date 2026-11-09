import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../core/theme.dart';
import '../core/api_client.dart';
import '../services/auth_service.dart';
import 'home_navigation_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController(text: AppConstants.demoEmail);
  final _passwordController = TextEditingController(text: AppConstants.demoPassword);
  final _authService = AuthService();
  final _client = ApiClient();

  bool _loading = false;
  String? _error;
  bool _showServerConfig = false;
  late TextEditingController _serverController;

  @override
  void initState() {
    super.initState();
    _serverController = TextEditingController(text: _client.baseUrl);
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _serverController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin({bool isDemo = false}) async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      if (isDemo) {
        await _authService.loginDemo();
      } else {
        await _authService.login(
          _emailController.text.trim(),
          _passwordController.text.trim(),
        );
      }

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeNavigationScreen()),
        );
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // App Brand Logo
                  Center(
                    child: Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        borderRadius: BorderRadius.circular(18),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.primary.withValues(alpha: 0.35),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 36),
                    ),
                  ),
                  const SizedBox(height: 20),

                  const Text(
                    'CareBridge',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.w800,
                      color: AppColors.textDark,
                      letterSpacing: -0.5,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    AppConstants.appTagline,
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 13.5, color: AppColors.textMuted),
                  ),
                  const SizedBox(height: 36),

                  if (_error != null) ...[
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.dangerBg,
                        border: Border.all(color: AppColors.dangerBorder),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.error_outline, color: AppColors.danger, size: 20),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              _error!,
                              style: const TextStyle(color: AppColors.danger, fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 18),
                  ],

                  // Email Input
                  const Text('Email Address', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      hintText: 'e.g. demo@carebridge.ai',
                      prefixIcon: Icon(Icons.email_outlined, size: 20),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Password Input
                  const Text('Password', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      hintText: 'Enter password',
                      prefixIcon: Icon(Icons.lock_outline, size: 20),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Submit Button
                  ElevatedButton(
                    onPressed: _loading ? null : () => _handleLogin(),
                    child: _loading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : const Text('Sign In'),
                  ),
                  const SizedBox(height: 12),

                  // 1-Tap Quick Demo Button
                  OutlinedButton.icon(
                    onPressed: _loading ? null : () => _handleLogin(isDemo: true),
                    icon: const Icon(Icons.flash_on_rounded, size: 18),
                    label: const Text('Quick Demo Login (Patient Account)'),
                  ),
                  const SizedBox(height: 28),

                  // Server Configuration Expander
                  Center(
                    child: TextButton.icon(
                      onPressed: () => setState(() => _showServerConfig = !_showServerConfig),
                      icon: Icon(
                        _showServerConfig ? Icons.keyboard_arrow_up : Icons.settings_outlined,
                        size: 16,
                      ),
                      label: Text(
                        _showServerConfig ? 'Hide Server URL' : 'Server Settings',
                        style: const TextStyle(fontSize: 12, color: AppColors.textLight),
                      ),
                    ),
                  ),

                  if (_showServerConfig) ...[
                    const SizedBox(height: 8),
                    TextField(
                      controller: _serverController,
                      decoration: InputDecoration(
                        labelText: 'API Base URL',
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.check, size: 18),
                          onPressed: () {
                            _client.baseUrl = _serverController.text.trim();
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Server API URL updated!')),
                            );
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        ActionChip(
                          label: const Text('Render Cloud', style: TextStyle(fontSize: 11)),
                          onPressed: () {
                            setState(() {
                              _serverController.text = AppConstants.defaultApiUrl;
                              _client.baseUrl = AppConstants.defaultApiUrl;
                            });
                          },
                        ),
                        ActionChip(
                          label: const Text('Localhost (8000)', style: TextStyle(fontSize: 11)),
                          onPressed: () {
                            setState(() {
                              _serverController.text = 'http://127.0.0.1:8000/api';
                              _client.baseUrl = 'http://127.0.0.1:8000/api';
                            });
                          },
                        ),
                        ActionChip(
                          label: const Text('Android Emulator', style: TextStyle(fontSize: 11)),
                          onPressed: () {
                            setState(() {
                              _serverController.text = AppConstants.localApiUrl;
                              _client.baseUrl = AppConstants.localApiUrl;
                            });
                          },
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 24),
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
                          'Smart Automation · Post Discharge Coordination',
                          style: TextStyle(fontSize: 10, color: AppColors.textMuted),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

