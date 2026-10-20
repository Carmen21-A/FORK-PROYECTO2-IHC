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
}
