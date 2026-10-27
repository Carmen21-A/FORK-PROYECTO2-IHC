import 'package:flutter_test/flutter_test.dart';
import 'package:presupuesto_estudiantil/utils/historial.dart';

void main() {
  group('1. Detalle del evento', () {
    test('arma el detalle de un gasto con descripcion', () {
      final detalle = armarDetalleEvento(
        tipo: 'gasto',
        monto: 50,
        categoria: 'Comida',
        descripcion: 'Almuerzo',
      );

      expect(detalle, 'Gasto 50 Bs · Comida · Almuerzo');
    });

    test('arma el detalle de un ingreso sin descripcion', () {
      final detalle = armarDetalleEvento(
        tipo: 'ingreso',
        monto: 200,
        categoria: 'Otros',
        descripcion: '',
      );

      expect(detalle, 'Ingreso 200 Bs · Otros');
    });

    test('ignora descripcion vacia o con espacios', () {
      final detalle = armarDetalleEvento(
        tipo: 'gasto',
        monto: 10,
        categoria: 'Transporte',
        descripcion: '   ',
      );

      expect(detalle, 'Gasto 10 Bs · Transporte');
    });
  });

  group('2. Orden reciente primero', () {
    test('ordena los eventos del mas nuevo al mas viejo', () {
      final eventos = [
        {'id': 'a', 'created_at': '2026-10-15T10:00:00Z'},
        {'id': 'c', 'created_at': '2026-10-17T09:30:00Z'},
        {'id': 'b', 'created_at': '2026-10-16T12:00:00Z'},
      ];

      final ordenados = ordenarRecientePrimero(eventos);

      expect(ordenados.map((e) => e['id']).toList(), ['c', 'b', 'a']);
    });
  });

  group('3. Caso vacio', () {
    test('devuelve lista vacia cuando no hay eventos', () {
      final ordenados = ordenarRecientePrimero([]);

      expect(ordenados, isEmpty);
    });
  });

  group('4. Filtrar historial', () {
    final eventosPrueba = [
      {
        'id': '1',
        'accion': 'creado',
        'detalle': 'Gasto 50 Bs · Comida · Almuerzo',
      },
      {
        'id': '2',
        'accion': 'editado',
        'detalle': 'Gasto 20 Bs · Transporte · Micro',
      },
      {'id': '3', 'accion': 'eliminado', 'detalle': 'Ingreso 100 Bs · Otros'},
    ];

    test('filtra por texto en detalle ignorando mayusculas', () {
      final resultado = filtrarHistorial(eventosPrueba, 'comida');

      expect(resultado.length, 1);
      expect(resultado.first['id'], '1');
    });

    test('filtra por accion', () {
      final resultado = filtrarHistorial(eventosPrueba, 'eliminado');

      expect(resultado.length, 1);
      expect(resultado.first['id'], '3');
    });

    test('devuelve lista vacia cuando nada coincide', () {
      final resultado = filtrarHistorial(eventosPrueba, 'cine');

      expect(resultado, isEmpty);
    });

    test('devuelve todos los eventos si la busqueda esta vacia', () {
      final resultado = filtrarHistorial(eventosPrueba, '   ');

      expect(resultado.length, 3);
    });
  });
}
