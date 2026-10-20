import 'package:supabase_flutter/supabase_flutter.dart';

import '../utils/historial.dart';
import 'historial_service.dart';

class MovementsService {
  final _db = Supabase.instance.client;
  final _historialService = HistorialService();

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

    final creado =
        await _db
            .from('movimientos')
            .insert({
              'user_id': user.id,
              'tipo': tipo,
              'monto': monto,
              'categoria': categoria,
              'descripcion': descripcion,
              'estado': _estadoInicial,
              'fecha': fecha.toIso8601String().split('T').first,
            })
            .select('id')
            .single();

    await _historialService.registrarEvento(
      accion: 'creado',
      movimientoId: creado['id'] as String?,
      detalle: armarDetalleEvento(
        tipo: tipo,
        monto: monto,
        categoria: categoria,
        descripcion: descripcion,
      ),
    );
  }

  Future<void> delete(String id) async {
    // Guardamos el evento antes de borrar el movimiento
    final movimiento =
        await _db.from('movimientos').select().eq('id', id).maybeSingle();

    if (movimiento != null) {
      try {
        await _historialService.registrarEvento(
          accion: 'eliminado',
          movimientoId: id,
          detalle: armarDetalleEvento(
            tipo: movimiento['tipo'] as String,
            monto: movimiento['monto'] as num,
            categoria: movimiento['categoria'] as String,
            descripcion: (movimiento['descripcion'] ?? '').toString(),
          ),
        );
      } catch (_) {}
    }

    await _db.from('movimientos').delete().eq('id', id);
  }

  Future<void> cambiarEstado(String id, String nuevoEstado) async {
    await _db.from('movimientos').update({'estado': nuevoEstado}).eq('id', id);

    await _historialService.registrarEvento(
      accion: 'cambio_estado',
      movimientoId: id,
      detalle: 'Estado cambiado a $nuevoEstado',
    );
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

    await _historialService.registrarEvento(
      accion: 'editado',
      movimientoId: id,
      detalle: armarDetalleEvento(
        tipo: tipo,
        monto: monto,
        categoria: categoria,
        descripcion: descripcion,
      ),
    );
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
}
