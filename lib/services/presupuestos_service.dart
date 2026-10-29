import 'package:supabase_flutter/supabase_flutter.dart'; //importa el paquete supabase_flutter
import '../utils/presupuesto_categoria.dart'; //importa el archivo presupuesto_categoria de utils

class PresupuestosService {
  //una clase llamada PresupuestosService
  final _db =
      Supabase
          .instance
          .client; //una constante privada _db == al cliente de la instancia de Supabase

  /// Obtiene todos los presupuestos asignados por categoría para un mes (formato 'YYYY-MM')
  /// Retorna un mapa con { 'Comida': 400.0, 'Transporte': 150.0, ... }
  Future<Map<String, double>> getPresupuestosMes(String mes) async {
    //una función asíncrona llamada getPresupuestosMes, que recibe un texto mes y en el futuro devuelve un mapa de texto a decimal
    final user =
        _db
            .auth
            .currentUser; //una constante user es igual al usuario actual de la autenticación de la base de datos
    if (user == null) return {}; //si user es nulo, retorna un mapa vacío

    // 1. Intentar con tabla dedicada presupuestos_categoria
    try {
      //intenta lo siguiente
      final data =
          await _db //una constante data es igual a esperar el resultado de la base de datos
              .from(
                'presupuestos_categoria',
              ) //desde la tabla presupuestos_categoria
              .select(
                'categoria, monto',
              ) //selecciona las columnas categoria y monto
              .eq('user_id', user.id) //donde user_id es igual al id del usuario
              .eq('mes', mes); //y donde mes es igual al mes recibido

      final resultado =
          <
            String,
            double
          >{}; //constante resultado == un mapa vacío de texto a decimal
      for (final row in data) {
        //para cada fila row en data
        final cat =
            row['categoria']
                as String; //constante cat == de categoria la fila como texto
        final monto =
            (row['monto'] as num)
                .toDouble(); //constante monto == la columna monto de la fila, como número, convertido a decimal
        resultado[cat] = monto; //en resultado, la clave cat es igual a monto
      }
      return resultado;
    } catch (_) {
      //si algo falla, atrapa el error (sin usarlo)
      // 2. Fallback a limites_mensuales con clave 'YYYY-MM#Categoria'
      try {
        //intenta lo siguiente
        final data = await _db //constante data == esperar de la base de datos
            .from('limites_mensuales') //desde la tabla limites_mensuales
            .select('mes, limite') //selecciona las columnas mes y limite
            .eq('user_id', user.id) //donde user_id == id del usuario
            .like(
              'mes',
              '$mes#%',
            ); //donde mes == "el mes recibido, numeral, y cualquier cosa"

        final resultado =
            <
              String,
              double
            >{}; //constante resultado == un mapa vacío de texto a decimal
        for (final row in data) {
          //para cada fila row en data
          final mesKey =
              row['mes']
                  as String; //constante mesKey == mes de la fila como texto
          final partes = mesKey.split(
            '#',
          ); //constante partes == mesKey dividido por numeral
          if (partes.length == 2 && partes[0] == mes) {
            //si cantidad de partes == 2 y la parte 0 es igual a mes
            final cat = partes[1]; //constante cat == la parte 1
            final monto =
                (row['limite'] as num)
                    .toDouble(); //constante monto == limite de la fila, como número, convertido a decimal
            resultado[cat] =
                monto; //en resultado, la clave cat es igual a monto
          }
        }
        return resultado;
      } catch (_) {
        //si algo falla, atrapa el error (sin usarlo)
        return {}; //retorna un mapa vacío
      }
    }
  }

  /// Guarda o actualiza el presupuesto de una categoría para un mes
  Future<void> savePresupuestoCategoria({
    //una función asíncrona llamada savePresupuestoCategoria, que en el futuro no devuelve nada, y recibe:
    required String mes, //un texto obligatorio mes
    required String categoria, //un texto obligatorio categoria
    required double monto, //un decimal obligatorio monto
  }) async {
    //y es asíncrona
    final user =
        _db
            .auth
            .currentUser; //constante user == el usuario actual de la autenticación de la base de datos
    if (user == null)
      throw Exception(
        'Usuario no autenticado',
      ); //si user es nulo, lanza un error "Usuario no autenticado"

    // 1. Intentar en tabla dedicada presupuestos_categoria
    try {
      //intenta lo siguiente
      final existing =
          await _db //constante existing == esperar de la base de datos
              .from(
                'presupuestos_categoria',
              ) //desde la tabla presupuestos_categoria
              .select('id') //selecciona la columna id
              .eq('user_id', user.id) //donde user_id es igual al id del usuario
              .eq('mes', mes) //y donde mes es igual al mes recibido
              .eq(
                'categoria',
                categoria,
              ) //y donde categoria es igual a la categoria recibida
              .maybeSingle(); //tal vez una sola fila (o nulo si no hay)

      if (existing != null) {
        //si existing no es nulo
        await _db //espera a la base de datos
            .from(
              'presupuestos_categoria',
            ) //desde la tabla presupuestos_categoria
            .update({
              //actualiza:
              'monto': monto, //la columna monto es igual a monto
              'updated_at':
                  DateTime.now()
                      .toUtc()
                      .toIso8601String(), //la columna updated_at es igual a la fecha y hora actual, en UTC, como texto ISO 8601
            }) //fin del update
            .eq('id', existing['id']); //donde id es igual al id de existing
      } else {
        //si no
        await _db.from('presupuestos_categoria').insert({
          //espera a la base de datos, desde la tabla presupuestos_categoria, inserta:
          'user_id': user.id, //la columna user_id es igual al id del usuario
          'mes': mes, //la columna mes es igual a mes
          'categoria': categoria, //la columna categoria es igual a categoria
          'monto': monto, //la columna monto es igual a monto
        });
      }
      return;
    } catch (_) {
      // 2. Fallback a limites_mensuales con formato 'YYYY-MM#Categoria'
      final claveMes =
          '$mes#$categoria'; //constante claveMes == "mes, numeral, categoria"
      final existing =
          await _db //constante existing == esperar de la base de datos
              .from('limites_mensuales') //desde la tabla limites_mensuales
              .select('id') //selecciona la columna id
              .eq('user_id', user.id) //donde user_id es igual al id del usuario
              .eq('mes', claveMes) //y donde mes es igual a claveMes
              .maybeSingle(); //tal vez una sola fila (o nulo si no hay)

      if (existing != null) {
        //si existing no es nulo
        await _db //espera a la base de datos
            .from('limites_mensuales') //desde la tabla limites_mensuales
            .update({'limite': monto}) //actualiza la columna limite a monto
            .eq('id', existing['id']); //donde id es igual al id de existing
      } else {
        //si no
        await _db.from('limites_mensuales').insert({
          //espera a la base de datos, desde la tabla limites_mensuales, inserta:
          'user_id': user.id, //la columna user_id es igual al id del usuario
          'mes': claveMes, //la columna mes es igual a claveMes
          'limite': monto, //la columna limite es igual a monto
        });
      }
    }
  }

  /// Elimina el presupuesto de una categoría para un mes específico
  Future<void> deletePresupuestoCategoria({
    //una función asíncrona llamada deletePresupuestoCategoria, que en el futuro no devuelve nada, y recibe:
    required String mes, //un texto obligatorio mes
    required String categoria, //un texto obligatorio categoria
  }) async {
    //y es asíncrona
    final user =
        _db
            .auth
            .currentUser; //una constante user es igual al usuario actual de la autenticación de la base de datos
    if (user == null) return; //si user es nulo, retorna (termina la función)

    try {
      //intenta lo siguiente
      await _db //espera a la base de datos
          .from(
            'presupuestos_categoria',
          ) //desde la tabla presupuestos_categoria
          .delete() //elimina
          .eq('user_id', user.id) //donde user_id es igual al id del usuario
          .eq('mes', mes) //y donde mes es igual al mes recibido
          .eq(
            'categoria',
            categoria,
          ); //y donde categoria es igual a la categoria recibida
    } catch (_) {
      //si algo falla, atrapa el error (sin usarlo)
      final claveMes =
          '$mes#$categoria'; //una constante claveMes es igual a "mes, numeral, categoria"
      await _db //espera a la base de datos
          .from('limites_mensuales') //desde la tabla limites_mensuales
          .delete() //elimina
          .eq('user_id', user.id) //donde user_id es igual al id del usuario
          .eq('mes', claveMes); //y donde mes es igual a claveMes
    }
  }

  /// Construye el resumen de presupuesto vs consumo combinando la base de datos y movimientos
  Future<ResumenPresupuestoMensual> getResumenMensual({
    //una función asíncrona llamada getResumenMensual, que en el futuro devuelve un ResumenPresupuestoMensual, y recibe:
    required String mes, //un texto obligatorio mes
    required List<Map<String, dynamic>>
    movimientos, //una lista obligatoria movimientos, de mapas de texto a cualquier tipo
  }) async {
    //y es asíncrona
    final presupuestos = await getPresupuestosMes(
      mes,
    ); //constante presupuestos == esperar getPresupuestosMes con mes
    return construirResumenMensual(
      //retorna construirResumenMensual con:
      mes: mes, //mes es igual a mes
      presupuestosPorCategoria:
          presupuestos, //presupuestosPorCategoria es igual a presupuestos
      movimientos: movimientos, //movimientos es igual a movimientos
    );
  }
}
