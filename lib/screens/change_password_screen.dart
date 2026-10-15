import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:presupuesto_estudiantil/widgets/app_drawer.dart';
import '../services/auth_service.dart';

class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({super.key});

  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _formularioId = GlobalKey<FormState>();
  final _passwordController1 = TextEditingController();
  final _passwordController2 = TextEditingController();
  final _authService = AuthService();

  Future<void> _handleChangePassword() async {
    if (!_formularioId.currentState!.validate()) return;

    try {
      await _authService.updatePassword(_passwordController1.text.trim());
      if (mounted) {
        context.go('/movements');
      }
    } catch (_) {
      _passwordController1.text = "";
      _passwordController2.text = "";
    }
  }

  @override
  void dispose() {
    _passwordController1.dispose();
    _passwordController2.dispose();
    super.dispose();
  }

  bool _mostrarPassword1 = false;
  bool _mostrarPassword2 = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: AppDrawer(),
      appBar: AppBar(title: const Text('Cambiar Contraseña')),
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
                  'Ingresa tu nueva contraseña',
                  style: AppTextStyle.boldBodyLarge,
                  textAlign: TextAlign.start,
                ),
              ),
              TextFormField(
                controller: _passwordController1,
                obscureText: _mostrarPassword1,
                decoration: InputDecoration(
                  hintText: 'password123',
                  suffixIcon: IconButton(
                    icon: Icon(
                      _mostrarPassword1
                          ? Icons.visibility_off
                          : Icons.visibility,
                    ),
                    onPressed:
                        () => setState(
                          () => _mostrarPassword1 = !_mostrarPassword1,
                        ),
                  ),
                ),
                validator:
                    (texto) =>
                        texto == null || texto.length < 6
                            ? 'Mínimo 6 caracteres'
                            : null,
              ),
              TextFormField(
                controller: _passwordController2,
                obscureText: _mostrarPassword2,
                decoration: InputDecoration(
                  hintText: 'password123',
                  suffixIcon: IconButton(
                    icon: Icon(
                      _mostrarPassword2
                          ? Icons.visibility_off
                          : Icons.visibility,
                    ),
                    onPressed:
                        () => setState(
                          () => _mostrarPassword2 = !_mostrarPassword2,
                        ),
                  ),
                ),
                validator: (texto) {
                  if (texto == null || texto.length < 6) {
                    return 'Mínimo 6 caracteres';
                  }
                  if (texto != _passwordController1.text) {
                    return "Las contraseñas no coinciden";
                  }
                  return null;
                },
              ),
              ElevatedButton(
                onPressed: _handleChangePassword,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 52),
                ),
                child: const Text('Actualizar Contraseña'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
