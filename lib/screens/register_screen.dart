import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/auth_service.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formularioId = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authService = AuthService();
  bool _mostrarPassword = false;

  Future<void> _handleRegister() async {
    if (!_formularioId.currentState!.validate()) return;

    try {
      await _authService.signUp(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
      );

      if (mounted) {
        context.go('/movements');
      }
    } on AuthException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e.message.contains('User already registered')
                  ? 'Este correo ya esta registrado, inicia sesion o usa otro correo.'
                  : e.message,
            ),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error al crear la cuenta, intenta nuevamente.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Crear Cuenta')),
      body: SafeArea(
        child: Padding(
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
                    hintText: 'ejemplo@gmail.com',
                  ),
                  validator:
                      (val) =>
                          val == null || val.isEmpty
                              ? 'Ingresa tu correo'
                              : null,
                ),
                SizedBox(
                  width: double.infinity,
                  child: Text(
                    'Contraseña',
                    style: AppTextStyle.boldBodyLarge,
                    textAlign: TextAlign.start,
                  ),
                ),
                TextFormField(
                  controller: _passwordController,
                  obscureText: _mostrarPassword,
                  decoration: InputDecoration(
                    hintText: 'password123',
                    suffixIcon: IconButton(
                      icon: Icon(
                        _mostrarPassword
                            ? Icons.visibility_off
                            : Icons.visibility,
                      ),
                      onPressed:
                          () => setState(
                            () => _mostrarPassword = !_mostrarPassword,
                          ),
                    ),
                  ),
                  validator: (texto) {
                    return (texto == null || texto.length < 6)
                        ? 'Mínimo 6 caracteres'
                        : null;
                  },
                ),
                ElevatedButton(
                  onPressed: _handleRegister,
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 52),
                  ),
                  child: const Text(
                    'Registrarse',
                    style: AppTextStyle.boldBodyMedium,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
