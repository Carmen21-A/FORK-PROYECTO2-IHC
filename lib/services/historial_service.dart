import 'package:supabase_flutter/supabase_flutter.dart';

class HistorialService {
  final _db = Supabase.instance.client;

  // Guarda un evento (append-only)
  Future<void> registrarEvento({
    required String accion,
    String? movimientoId,
    required String detalle,
  }) async {
    final user = _db.auth.currentUser;
    if (user == null) return;

    await _db.from('historial').insert({
      'user_id': user.id,
      'accion': accion,
      'movimiento_id': movimientoId,
      'detalle': detalle,
    });
  }

  // Trae los eventos del usuario, reciente primero
  Future<List<Map<String, dynamic>>> getHistorial() async {
    final user = _db.auth.currentUser;
    if (user == null) return [];

    final data = await _db
        .from('historial')
        .select()
        .eq('user_id', user.id)
        .order('created_at', ascending: false);

    return List<Map<String, dynamic>>.from(data);
  }
}
