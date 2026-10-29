import 'package:supabase_flutter/supabase_flutter.dart';
import '../utils/presupuesto_categoria.dart';

class PresupuestosService {
  final _db = Supabase.instance.client;

  /// Obtiene todos los presupuestos asignados por categoría para un mes (formato 'YYYY-MM')
  /// Retorna un mapa con { 'Comida': 400.0, 'Transporte': 150.0, ... }
  Future<Map<String, double>> getPresupuestosMes(String mes) async {
    //Una función asíncrona llamada getPresupuestosMes, que recibe un texto mes y en el futuro devuelve un mapa de texto a decimal.
    final user =
        _db
            .auth
            .currentUser; //Una constante user es igual al usuario actual de la autenticación de la base de datos.
    if (user == null) return {}; //Si usuario = vacio, devuelve un mapa vacío.

    // 1. Intentar con tabla dedicada presupuestos_categoria
    try {
      final data = await _db //constante data = espera resultado de BD
          .from(
            'presupuestos_categoria',
          ) //desde la tabla presupuestos_categoria
          .select(
            'categoria, monto',
          ) //selecciona las columnas categoria y monto
          .eq('user_id', user.id) //
          .eq('mes', mes); //

      final resultado = <String, double>{};
      for (final row in data) {
        final cat = row['categoria'] as String;
        final monto = (row['monto'] as num).toDouble();
        resultado[cat] = monto;
      }
      return resultado;
    } catch (_) {
      // 2. Fallback a limites_mensuales con clave 'YYYY-MM#Categoria'
      try {
        final data = await _db
            .from('limites_mensuales')
            .select('mes, limite')
            .eq('user_id', user.id)
            .like('mes', '$mes#%');

        final resultado = <String, double>{};
        for (final row in data) {
          final mesKey = row['mes'] as String;
          final partes = mesKey.split('#');
          if (partes.length == 2 && partes[0] == mes) {
            final cat = partes[1];
            final monto = (row['limite'] as num).toDouble();
            resultado[cat] = monto;
          }
        }
        return resultado;
      } catch (_) {
        return {};
      }
    }
  }

  /// Guarda o actualiza el presupuesto de una categoría para un mes
  Future<void> savePresupuestoCategoria({
    required String mes,
    required String categoria,
    required double monto,
  }) async {
    final user = _db.auth.currentUser;
    if (user == null) throw Exception('Usuario no autenticado');

    // 1. Intentar en tabla dedicada presupuestos_categoria
    try {
      final existing =
          await _db
              .from('presupuestos_categoria')
              .select('id')
              .eq('user_id', user.id)
              .eq('mes', mes)
              .eq('categoria', categoria)
              .maybeSingle();

      if (existing != null) {
        await _db
            .from('presupuestos_categoria')
            .update({
              'monto': monto,
              'updated_at': DateTime.now().toUtc().toIso8601String(),
            })
            .eq('id', existing['id']);
      } else {
        await _db.from('presupuestos_categoria').insert({
          'user_id': user.id,
          'mes': mes,
          'categoria': categoria,
          'monto': monto,
        });
      }
      return;
    } catch (_) {
      // 2. Fallback a limites_mensuales con formato 'YYYY-MM#Categoria'
      final claveMes = '$mes#$categoria';
      final existing =
          await _db
              .from('limites_mensuales')
              .select('id')
              .eq('user_id', user.id)
              .eq('mes', claveMes)
              .maybeSingle();

      if (existing != null) {
        await _db
            .from('limites_mensuales')
            .update({'limite': monto})
            .eq('id', existing['id']);
      } else {
        await _db.from('limites_mensuales').insert({
          'user_id': user.id,
          'mes': claveMes,
          'limite': monto,
        });
      }
    }
  }

  /// Elimina el presupuesto de una categoría para un mes específico
  Future<void> deletePresupuestoCategoria({
    required String mes,
    required String categoria,
  }) async {
    final user = _db.auth.currentUser;
    if (user == null) return;

    try {
      await _db
          .from('presupuestos_categoria')
          .delete()
          .eq('user_id', user.id)
          .eq('mes', mes)
          .eq('categoria', categoria);
    } catch (_) {
      final claveMes = '$mes#$categoria';
      await _db
          .from('limites_mensuales')
          .delete()
          .eq('user_id', user.id)
          .eq('mes', claveMes);
    }
  }

  /// Construye el resumen de presupuesto vs consumo combinando la base de datos y movimientos
  Future<ResumenPresupuestoMensual> getResumenMensual({
    required String mes,
    required List<Map<String, dynamic>> movimientos,
  }) async {
    final presupuestos = await getPresupuestosMes(mes);
    return construirResumenMensual(
      mes: mes,
      presupuestosPorCategoria: presupuestos,
      movimientos: movimientos,
    );
  }
}
