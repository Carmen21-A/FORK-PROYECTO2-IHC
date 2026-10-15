import 'package:flutter_test/flutter_test.dart';
import 'package:presupuesto_estudiantil/utils/movimientos_filtros.dart';

void main() {
  final List<Map<String, dynamic>> movimientos = [
    {
      'fecha': '2026-10-01',
      'tipo': 'gasto',
      'categoria': 'Comida',
      'estado': 'pagado',
      'monto': 100.0,
      'descripcion': 'Almuerzo universidad',
    },
    {
      'fecha': '2026-10-05',
      'tipo': 'gasto',
      'categoria': 'Transporte',
      'estado': 'pendiente',
      'monto': 50.0,
      'descripcion': 'Pasaje bus',
    },
    {
      'fecha': '2026-10-10',
      'tipo': 'ingreso',
      'categoria': 'Otros',
      'estado': 'pagado',
      'monto': 1000.0,
      'descripcion': 'Beca',
    },
    {
      'fecha': '2026-09-20',
      'tipo': 'gasto',
      'categoria': 'Comida',
      'estado': 'pagado',
      'monto': 30.0,
      'descripcion': 'Cena',
    },
  ];

  group('1. Casos con resultados', () {
    test('filtra por coincidencia parcial en la descripcion', () {
      final filtrados = filtrarMovimientos(movimientos, texto: 'almu');

      expect(filtrados.length, 1);
      expect(filtrados.first['descripcion'], 'Almuerzo universidad');
    });

    test('filtra por tipo', () {
      final filtrados = filtrarMovimientos(movimientos, tipo: 'ingreso');

      expect(filtrados.length, 1);
      expect(filtrados.first['descripcion'], 'Beca');
    });
  });

  group('2. Caso sin resultados', () {
    test('devuelve lista vacia cuando nada coincide', () {
      final filtrados = filtrarMovimientos(movimientos, texto: 'zzzz');

      expect(filtrados, isEmpty);
    });
  });

  group('3. Combinacion de varios filtros', () {
    test('combina tipo, categoria y estado', () {
      final filtrados = filtrarMovimientos(
        movimientos,
        tipo: 'gasto',
        categoria: 'Comida',
        estado: 'pagado',
      );

      // Octubre y septiembre
      expect(filtrados.length, 2);
    });

    test('combina texto, tipo y rango de fechas', () {
      final filtrados = filtrarMovimientos(
        movimientos,
        texto: 'pasaje',
        tipo: 'gasto',
        desde: DateTime(2026, 10, 1),
        hasta: DateTime(2026, 10, 31),
      );

      expect(filtrados.length, 1);
      expect(filtrados.first['descripcion'], 'Pasaje bus');
    });
  });

  group('4. Total coincide con la suma de los filtrados', () {
    test('el total es la suma de los montos filtrados', () {
      final filtrados = filtrarMovimientos(
        movimientos,
        tipo: 'gasto',
        categoria: 'Comida',
      );
      final total = calcularMontoTotalMovimientos(filtrados);

      // 100 + 30
      expect(total, 130.0);

      final sumaManual = filtrados.fold<double>(
        0.0,
        (sum, m) => sum + (m['monto'] as num).toDouble(),
      );
      expect(total, sumaManual);
    });
  });

  group('5. Totales separados por tipo', () {
    final conCancelado = [
      {
        'fecha': '2026-10-01',
        'tipo': 'gasto',
        'categoria': 'Comida',
        'estado': 'pagado',
        'monto': 100.0,
        'descripcion': 'Almuerzo',
      },
      {
        'fecha': '2026-10-02',
        'tipo': 'gasto',
        'categoria': 'Ocio',
        'estado': 'cancelado',
        'monto': 200.0,
        'descripcion': 'Cine',
      },
      {
        'fecha': '2026-10-03',
        'tipo': 'ingreso',
        'categoria': 'Otros',
        'estado': 'pagado',
        'monto': 500.0,
        'descripcion': 'Beca',
      },
    ];

    test('el total de gastos no incluye cancelados', () {
      expect(calcularTotalGastos(conCancelado), 100.0);
    });

    test('el total de ingresos no incluye cancelados', () {
      expect(calcularTotalIngresos(conCancelado), 500.0);
    });
  });
}
