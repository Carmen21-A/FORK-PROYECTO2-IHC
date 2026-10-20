import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../services/auth_service.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:presupuesto_estudiantil/design_system/color_styles.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: BoxDecoration(color: ColorStyles.primaryBase),
            child: Text(
              'Menú',
              style: AppTextStyle.boldBodyLarge.copyWith(
                color: ColorStyles.textInverse,
              ),
            ),
          ),
          ListTile(
            title: const Text('Movimientos'),
            onTap: () {
              Navigator.pop(context); // cierra el drawer
              context.go('/movements');
            },
          ),
          ListTile(
            title: const Text('Historial'),
            onTap: () {
              Navigator.pop(context);
              context.go('/history');
            },
          ),
          ListTile(
            title: const Text('Cambiar contraseña'),
            onTap: () {
              Navigator.pop(context);
              context.go('/change-password');
            },
          ),
          ListTile(
            title: const Text('Ayuda'),
            onTap: () {
              Navigator.pop(context);
              showDialog(
                context: context,
                builder:
                    (context) => AlertDialog(
                      title: const Text('Acerca de la aplicación'),
                      content: const Text(
                        'El Presupuesto Estudiantil te ayuda a registrar tus gastos e ingresos y controlar que no superes tu limite mensual.',
                      ),
                      actions: [
                        OutlinedButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('Cerrar'),
                        ),
                      ],
                    ),
              );
            },
          ),

          const Divider(),
          ListTile(
            title: const Text('Cerrar sesión'),
            onTap: () async {
              Navigator.pop(context);
              await AuthService().signOut();
              if (context.mounted) context.go('/');
            },
          ),
        ],
      ),
    );
  }
}
