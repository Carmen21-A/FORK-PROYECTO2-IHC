import 'package:flutter_test/flutter_test.dart';

import 'package:presupuesto_estudiantil/utils/limite_mensual.dart';

void main() {
  group('1. Validacion del texto del limite', () {
    test('Tiene que retornar null (valido) para montos correctos', () {
      expect(validarMontoLimite('500'), isNull);
      expect(validarMontoLimite('100.5'), isNull);
    });

    test('No debe dejar pasar cadenas vacias o nulas', () {
      expect(validarMontoLimite(''), equals('El límite no debe estar vacio'));
      expect(validarMontoLimite(null), equals('El límite no debe estar vacio'));
    });

    test('No debe dejar pasar letras o textos mezclados con numeros', () {
      expect(
        validarMontoLimite('abcasdasdsad'),
        equals('No se permite letras, ingresa un numero valido'),
      );
      expect(
        validarMontoLimite('abcasd123213'),
        equals('No se permite letras, ingresa un numero valido'),
      );
    });

    test('No debe dejar pasar ceros o numeros negativos', () {
      expect(
        validarMontoLimite('0'),
        equals('El monto tiene que ser mayor a 0'),
      );
      expect(
        validarMontoLimite('-50'),
        equals('El monto tiene que ser mayor a 0'),
      );
    });
  });

  group('2. Limite menor a lo ya gastado', () {
    test('Debe devolver true si el nuevo limite es menor al gasto actual', () {
      final resultado = esLimiteMenorAGasto(200.0, 300.0);
      expect(resultado, isTrue);
    });

    test(
      'Debe devolver false si el nuevo limite es mayor o igual al gasto actual',
      () {
        final resultado = esLimiteMenorAGasto(500.0, 300.0);
        expect(resultado, isFalse);
      },
    );
  });

  group('3. Para no superar el limite mensual', () {
    test(
      'Debe devolver true si al agregar el nuevo gasto se supera el limite',
      () {
        final supera = superaLimiteMensual(
          gastoActualDelMes: 400.0,
          nuevoGasto: 150.0,
          limite: 500.0,
        );
        expect(supera, isTrue);
      },
    );

    test(
      'Debe devolver false si el gasto entra dentro del limite permitido',
      () {
        final supera = superaLimiteMensual(
          gastoActualDelMes: 400.0,
          nuevoGasto: 50.0,
          limite: 500.0,
        );
        expect(supera, isFalse);
      },
    );

    test('Debe devolver el mensaje de error al exceder el limite', () {
      final mensaje = getMensajesErrorLimiteMensual(
        nuevoMonto: 150.0,
        gastoActual: 400.0,
        limite: 500.0,
      );
      expect(mensaje, contains('al editar se excedera el limite mensual'));
    });
  });

  group('4. Calcular el gasto total del mes', () {
    final List<Map<String, dynamic>> movimientosMock = [
      {
        'fecha': '2026-10-01',
        'tipo': 'gasto',
        'estado': 'pagado',
        'monto': 100.0,
      },
      {
        'fecha': '2026-10-05',
        'tipo': 'gasto',
        'estado': 'pendiente',
        'monto': 50.0,
      },
      {
        'fecha': '2026-10-10',
        'tipo': 'gasto',
        'estado': 'cancelado',
        'monto': 200.0,
      },
      {
        'fecha': '2026-10-12',
        'tipo': 'ingreso',
        'estado': 'pagado',
        'monto': 1000.0,
      },
      {
        'fecha': '2026-09-15',
        'tipo': 'gasto',
        'estado': 'pagado',
        'monto': 300.0,
      },
    ];

    test(
      'Debe sumar solo los gastos validos del mes y excluir cancelados e ingresos',
      () {
        final totalOctubre = calcularGastoTotalMes(movimientosMock, '2026-10');

        // Solo deberia sumar 100.0 + 50.0 = 150.0
        expect(totalOctubre, equals(150.0));
      },
    );
  });
}
