import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import '../services/auth_service.dart';

class ResetPasswordScreen extends StatefulWidget {
  const ResetPasswordScreen({super.key});

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _formularioId = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _authService = AuthService();

  Future<void> _handleResetPassword() async {
    if (!_formularioId.currentState!.validate()) return;

    try {
      await _authService.resetPasswordForEmail(_emailController.text.trim());

      if (mounted) {
        context.go('/login');
      }
    } catch (_) {
      _emailController.text = "";
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recuperar Contraseña')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formularioId,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                width: double.infinity,
                child: Text(
                  'Correo electrónico',
                  style: AppTextStyle.boldBodyLarge,
                  textAlign: TextAlign.start,
                ),
              ),
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  hintText: 'Ingresa tu correo registrado',
                ),
                validator:
                    (val) =>
                        val == null || val.isEmpty ? 'Ingresa tu correo' : null,
              ),
              ElevatedButton(
                onPressed: _handleResetPassword,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 52),
                ),
                child: const Text('Enviar Solicitud'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
