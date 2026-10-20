import 'package:flutter/material.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:presupuesto_estudiantil/design_system/color_styles.dart';

final appTheme = ThemeData(
  colorScheme: ColorScheme.fromSeed(seedColor: ColorStyles.primaryBase),
  // estilos para los botones normales
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ButtonStyle(
      backgroundColor: WidgetStatePropertyAll(ColorStyles.primaryBase),
      foregroundColor: WidgetStatePropertyAll(ColorStyles.textInverse),
      textStyle: WidgetStatePropertyAll(AppTextStyle.boldBodyMedium),
    ),
  ),
  // estilos para los botones sin outline
  textButtonTheme: TextButtonThemeData(
    style: ButtonStyle(
      foregroundColor: WidgetStatePropertyAll(ColorStyles.primary100),
      textStyle: WidgetStatePropertyAll(AppTextStyle.boldBodyMedium),
    ),
  ),
  // estilos para los botones con outiline y sin fondo
  outlinedButtonTheme: OutlinedButtonThemeData(
    style: ButtonStyle(
      textStyle: WidgetStatePropertyAll(AppTextStyle.boldBodyMedium),
      side: WidgetStatePropertyAll(
        const BorderSide(color: ColorStyles.primaryBase, width: 1.5),
      ),
      shape: WidgetStatePropertyAll(
        RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
  ),
  // estilos para los campos de text (TextFormField)
  inputDecorationTheme: InputDecorationTheme(
    border: const OutlineInputBorder(),
    focusedBorder: OutlineInputBorder(
      borderSide: BorderSide(color: ColorStyles.primaryBase, width: 2),
    ),
  ),
  // estilos del picker
  datePickerTheme: DatePickerThemeData(
    headerBackgroundColor: ColorStyles.primaryBase,
    headerForegroundColor: ColorStyles.textInverse,
    backgroundColor: ColorStyles.textInverse,
    cancelButtonStyle: OutlinedButton.styleFrom(
      foregroundColor: ColorStyles.primaryBase,
    ),
    confirmButtonStyle: OutlinedButton.styleFrom(
      foregroundColor: ColorStyles.successDefault,
    ),
    dayBackgroundColor: WidgetStatePropertyAll(ColorStyles.primaryBase),
    dayForegroundColor: WidgetStatePropertyAll(ColorStyles.textInverse),
    todayBorder: BorderSide(color: ColorStyles.primaryBase, width: 1),
    todayForegroundColor: WidgetStatePropertyAll(ColorStyles.primaryBase),
    weekdayStyle: const TextStyle(color: ColorStyles.grayBase),
    dayStyle: const TextStyle(color: ColorStyles.textBase),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
  ),
  // estilos drawer (Meny Bar)
  drawerTheme: DrawerThemeData(backgroundColor: Colors.white),
);
