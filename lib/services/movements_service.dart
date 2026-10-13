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

  // Combina busqueda y filtros en una sola consulta a Supabase
  Future<List<Map<String, dynamic>>> buscarConFiltros({
    String? texto,
    String? tipo,
    String? categoria,
    String? estado,
    DateTime? desde,
    DateTime? hasta,
  }) async {
    final user = _db.auth.currentUser;
    if (user == null) return [];

    var consulta = _db.from('movimientos').select().eq('user_id', user.id);

    // Busqueda por descripcion con coincidencia parcial
    if (texto != null && texto.trim().isNotEmpty) {
      consulta = consulta.ilike('descripcion', '%${texto.trim()}%');
    }

    if (tipo != null) {
      consulta = consulta.eq('tipo', tipo);
    }
    if (categoria != null) {
      consulta = consulta.eq('categoria', categoria);
    }
    if (estado != null) {
      consulta = consulta.eq('estado', estado);
    }

    if (desde != null) {
      consulta = consulta.gte(
        'fecha',
        desde.toIso8601String().split('T').first,
      );
    }
    if (hasta != null) {
      consulta = consulta.lte(
        'fecha',
        hasta.toIso8601String().split('T').first,
      );
    }

    final data = await consulta
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
