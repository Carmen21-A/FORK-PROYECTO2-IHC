import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:presupuesto_estudiantil/design_system/spacing_tokens.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:presupuesto_estudiantil/design_system/color_styles.dart';
import '../env.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //El SafeArea ayuda a que el contenido se muestre correctamente en cualquier dispositivo
      //sin tapar ningun elemento importante de la pantalla
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),

          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Column(
                spacing: SpacingTokens.xS,
                children: [
                  Text(
                    '¡Bienvenido a tu ${Env.appName}!',
                    style: AppTextStyle.boldBodyLarge,
                    textAlign: TextAlign.center,
                  ),

                  Image.asset(
                    'assets/icons/v1/icon_no_background.png',
                    width: 150,
                  ),

                  Text(
                    'Una aplicación que te ayuda a llevar tus cuentas estudiantiles',
                    style: AppTextStyle.regularMicro.copyWith(
                      color: ColorStyles.textSecondary,
                    ),
                  ),
                ],
              ),
              Column(
                spacing: SpacingTokens.xS,
                children: [
                  // const Spacer(),
                  //  login
                  ElevatedButton(
                    onPressed: () {
                      context.push('/login');
                    },
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 52),
                    ),
                    child: const Text(
                      'Iniciar Sesión',
                      style: AppTextStyle.boldBodyMedium,
                    ),
                  ),

                  // registro
                  OutlinedButton(
                    onPressed: () {
                      context.push('/register');
                    },
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 52),
                    ),
                    child: Text(
                      'Crear una cuenta',
                      style: AppTextStyle.boldBodyMedium.copyWith(
                        color: ColorStyles.primaryBase,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
