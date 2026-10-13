import 'package:supabase_flutter/supabase_flutter.dart';

class MovementsService {
  final _db = Supabase.instance.client;

  Future<List<Map<String, dynamic>>> getAll() async {
    final user = _db.auth.currentUser;
    if (user == null) return [];

    final data = await _db
        .from('movimientos')
        .select()
        .eq('user_id', user.id)
        .order('fecha', ascending: true)
        .order('created_at', ascending: true);

    return List<Map<String, dynamic>>.from(data);
  }

  final String _estadoInicial = 'pendiente';

  Future<void> create({
    required String tipo,
    required double monto,
    required String categoria,
    required DateTime fecha,
    required String descripcion,
  }) async {
    final user = _db.auth.currentUser;
    if (user == null) return;

    await _db.from('movimientos').insert({
      'user_id': user.id,
      'tipo': tipo,
      'monto': monto,
      'categoria': categoria,
      'descripcion': descripcion,
      'estado': _estadoInicial,
      'fecha': fecha.toIso8601String().split('T').first,
    });
  }

  Future<void> delete(String id) async {
    await _db.from('movimientos').delete().eq('id', id);
  }

  Future<void> cambiarEstado(String id, String nuevoEstado) async {
    await _db.from('movimientos').update({'estado': nuevoEstado}).eq('id', id);
  }

  Future<void> update({
    required String id,
    required String tipo,
    required double monto,
    required String categoria,
    required DateTime fecha,
    required String descripcion,
  }) async {
    await _db
        .from('movimientos')
        .update({
          'tipo': tipo,
          'monto': monto,
          'categoria': categoria,
          'descripcion': descripcion,
          'fecha': fecha.toIso8601String().split('T').first,
        })
        .eq('id', id);
  }
}
