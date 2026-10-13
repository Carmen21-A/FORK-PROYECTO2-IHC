import 'package:supabase_flutter/supabase_flutter.dart';

class LimitesService {
  final _db = Supabase.instance.client;

  Future<double?> getLimit(String mes) async {
    final user = _db.auth.currentUser;
    if (user == null) return null;

    final response =
        await _db
            .from('limites_mensuales')
            .select('limite')
            .eq('user_id', user.id)
            .eq('mes', mes)
            .maybeSingle();

    if (response == null || response['limite'] == null) {
      return null;
    }

    return (response['limite'] as num).toDouble();
  }

  Future<void> saveMonthLimit({
    required String mes,
    required double limite,
  }) async {
    final user = _db.auth.currentUser;
    if (user == null) throw Exception('Usuario no autenticado');

    final existing =
        await _db
            .from('limites_mensuales')
            .select('id')
            .eq('user_id', user.id)
            .eq('mes', mes)
            .maybeSingle();

    if (existing != null) {
      await _db
          .from('limites_mensuales')
          .update({'limite': limite})
          .eq('id', existing['id']);
    } else {
      await _db.from('limites_mensuales').insert({
        'user_id': user.id,
        'mes': mes,
        'limite': limite,
      });
    }
  }
}
