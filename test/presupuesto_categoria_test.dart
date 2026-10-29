import 'package:flutter_test/flutter_test.dart';
import 'package:presupuesto_estudiantil/utils/presupuesto_categoria.dart';

void main() {
  /// Agrupación de pruebas para verificar la validación del texto ingresado
  group('1. Validación de monto de presupuesto por categoría', () {
    test('Acepta montos numéricos válidos mayores a cero', () {
      /// Se comprueba que '350' devuelva null (es decir, que no haya error)
      expect(validarMontoPresupuesto('350'), isNull);

      /// Se comprueba que un decimal como '150.50' devuelva null
      expect(validarMontoPresupuesto('150.50'), isNull);

      /// Se comprueba que un número con espacios alrededor como '  500  ' se limpie y sea válido
      expect(validarMontoPresupuesto('  500  '), isNull);
    });

    test('Rechaza entradas vacías o nulas', () {
      /// Se comprueba que un texto vacío '' devuelva el mensaje de error correspondiente
      expect(
        validarMontoPresupuesto(''),
        equals('El presupuesto no debe estar vacío'),
      );

      /// Se comprueba que puros espacios '   ' también se detecten como vacíos
      expect(
        validarMontoPresupuesto('   '),
        equals('El presupuesto no debe estar vacío'),
      );

      /// Se comprueba que un valor nulo devuelva el mensaje de error
      expect(
        validarMontoPresupuesto(null),
        equals('El presupuesto no debe estar vacío'),
      );
    });

    test('Rechaza letras o caracteres no numéricos', () {
      /// Se comprueba que un texto con solo letras como 'abc' retorne error
      expect(
        validarMontoPresupuesto('abc'),
        equals('No se permiten letras, ingresa un número válido'),
      );

      /// Se comprueba que un número mezclado con texto como '100Bs' retorne error
      expect(
        validarMontoPresupuesto('100Bs'),
        equals('No se permiten letras, ingresa un número válido'),
      );
    });

    test('Rechaza montos iguales o menores a 0', () {
      /// Se comprueba que el valor '0' retorne error exigiendo mayor a cero
      expect(
        validarMontoPresupuesto('0'),
        equals('El presupuesto debe ser mayor a 0'),
      );

      /// Se comprueba que un número negativo como '-20' retorne error
      expect(
        validarMontoPresupuesto('-20'),
        equals('El presupuesto debe ser mayor a 0'),
      );
    });
  });

  /// Agrupación de pruebas para verificar el cálculo del dinero consumido por categoría
  group('2. Cálculo de consumo de gastos por categoría', () {
    /// Lista simulada de movimientos para las pruebas
    final movimientos = [
      {
        /// Movimiento 1: Gasto en Comida del mes 10 por 50 Bs (debe sumarse)
        'fecha': '2026-10-02',
        'tipo': 'gasto',
        'categoria': 'Comida',
        'estado': 'pagado',
        'monto': 50.0,
      },
      {
        /// Movimiento 2: Gasto en Comida del mes 10 por 75 Bs en estado pendiente (debe sumarse)
        'fecha': '2026-10-05',
        'tipo': 'gasto',
        'categoria': 'Comida',
        'estado': 'pendiente',
        'monto': 75.0,
      },
      {
        /// Movimiento 3: Gasto cancelado por 100 Bs (NO debe sumarse porque fue cancelado)
        'fecha': '2026-10-08',
        'tipo': 'gasto',
        'categoria': 'Comida',
        'estado': 'cancelado',
        'monto': 100.0,
      },
      {
        /// Movimiento 4: Ingreso de dinero por 500 Bs (NO debe sumarse porque no es gasto)
        'fecha': '2026-10-10',
        'tipo': 'ingreso',
        'categoria': 'Comida',
        'estado': 'pagado',
        'monto': 500.0,
      },
      {
        /// Movimiento 5: Gasto de Transporte por 30 Bs (pertenece a otra categoría)
        'fecha': '2026-10-12',
        'tipo': 'gasto',
        'categoria': 'Transporte',
        'estado': 'pagado',
        'monto': 30.0,
      },
      {
        /// Movimiento 6: Gasto de septiembre (NO debe sumarse porque es de otro mes)
        'fecha': '2026-09-20',
        'tipo': 'gasto',
        'categoria': 'Comida',
        'estado': 'pagado',
        'monto': 200.0,
      },
    ];

    test('Calcula correctamente el consumo de una categoría en el mes', () {
      /// Se calcula el gasto real de Comida en el mes 2026-10
      final gastoComida = calcularGastoCategoria(
        movimientos: movimientos,
        mes: '2026-10',
        categoria: 'Comida',
      );

      /// Se verifica que la suma sea exactamente 50.0 + 75.0 = 125.0
      expect(gastoComida, equals(125.0));
    });

    test('Calcula correctamente el consumo de Transporte', () {
      /// Se calcula el gasto de Transporte en el mes 2026-10
      final gastoTransporte = calcularGastoCategoria(
        movimientos: movimientos,
        mes: '2026-10',
        categoria: 'Transporte',
      );

      /// Se verifica que solo sume el único movimiento de Transporte por 30.0 Bs
      expect(gastoTransporte, equals(30.0));
    });

    test('Devuelve 0 si no hay gastos en la categoría', () {
      /// Se calcula el gasto de Estudios (no tiene movimientos en la lista)
      final gastoEstudios = calcularGastoCategoria(
        movimientos: movimientos,
        mes: '2026-10',
        categoria: 'Estudios',
      );

      /// Se comprueba que devuelva 0.0
      expect(gastoEstudios, equals(0.0));
    });

    test('Cuenta cantidad de movimientos válidos de la categoría', () {
      /// Se cuenta cuántos movimientos válidos de Comida hubo en octubre
      final count = contarMovimientosCategoria(
        movimientos: movimientos,
        mes: '2026-10',
        categoria: 'Comida',
      );

      /// Se comprueba que fueron exactamente 2 movimientos (50 Bs y 75 Bs)
      expect(count, equals(2));
    });
  });

  /// Agrupación de pruebas para porcentajes, saldos y estados de semáforo
  group('3. Estado y porcentaje de consumo del presupuesto', () {
    test('Calcula porcentaje correctamente', () {
      /// Se verifica que 250 de 500 dé exactamente 0.5 (50%)
      expect(calcularPorcentajeConsumo(500.0, 250.0), equals(0.5));

      /// Se comprueba que si el presupuesto es 0, no divida por cero y devuelva 0.0
      expect(calcularPorcentajeConsumo(0.0, 100.0), equals(0.0));

      /// Se comprueba que si gastó 300 de 200, dé 1.5 (150% - excedido)
      expect(calcularPorcentajeConsumo(200.0, 300.0), equals(1.5));
    });

    test('Calcula saldo restante positivo y negativo (exceso)', () {
      /// Se comprueba que 500 presupuestado menos 200 gastado deje un saldo positivo de 300
      expect(calcularSaldoRestante(500.0, 200.0), equals(300.0));

      /// Se comprueba que 200 presupuestado menos 250 gastado dé -50 (50 Bs de exceso)
      expect(calcularSaldoRestante(200.0, 250.0), equals(-50.0));
    });

    test('Determina EstadoPresupuesto.sinPresupuesto', () {
      /// Si el presupuesto fijado es 0.0
      final estado = obtenerEstadoPresupuesto(
        presupuestado: 0.0,
        consumido: 50.0,
      );

      /// Se comprueba que el estado sea sinPresupuesto
      expect(estado, equals(EstadoPresupuesto.sinPresupuesto));
    });

    test('Determina EstadoPresupuesto.optimo cuando gasto < 80%', () {
      /// Gasto de 350 sobre 500 representa un 70% (< 80%)
      final estado = obtenerEstadoPresupuesto(
        presupuestado: 500.0,
        consumido: 350.0,
      );

      /// Se comprueba que el estado sea optimo
      expect(estado, equals(EstadoPresupuesto.optimo));
    });

    test('Determina EstadoPresupuesto.alerta cuando gasto está entre 80% y 100%', () {
      /// Gasto de 420 sobre 500 representa un 84% (>= 80% y <= 100%)
      final estado = obtenerEstadoPresupuesto(
        presupuestado: 500.0,
        consumido: 420.0,
      );

      /// Se comprueba que el estado sea alerta
      expect(estado, equals(EstadoPresupuesto.alerta));
    });

    test('Determina EstadoPresupuesto.excedido cuando gasto > 100%', () {
      /// Gasto de 550 sobre 500 representa un 110% (> 100%)
      final estado = obtenerEstadoPresupuesto(
        presupuestado: 500.0,
        consumido: 550.0,
      );

      /// Se comprueba que el estado sea excedido
      expect(estado, equals(EstadoPresupuesto.excedido));
    });
  });

  /// Agrupación de pruebas para el resumen mensual consolidado
  group('4. Resumen general mensual por categorías', () {
    /// Movimientos de prueba con distintas categorías
    final movimientos = [
      {
        'fecha': '2026-10-01',
        'tipo': 'gasto',
        'categoria': 'Transporte',
        'estado': 'pagado',
        'monto': 120.0,
      },
      {
        'fecha': '2026-10-02',
        'tipo': 'gasto',
        'categoria': 'Comida',
        'estado': 'pagado',
        'monto': 450.0,
      },
      {
        'fecha': '2026-10-03',
        'tipo': 'gasto',
        'categoria': 'Estudios',
        'estado': 'pagado',
        'monto': 160.0,
      },
    ];

    /// Presupuestos configurados
    final presupuestos = {
      'Transporte': 100.0, // Consumido 120 -> EXCEDIDO
      'Comida': 500.0,     // Consumido 450 -> ALERTA (90%)
      'Estudios': 300.0,   // Consumido 160 -> OPTIMO (53.3%)
      'Ocio': 150.0,       // Consumido 0   -> OPTIMO (0%)
    };

    test('Construye resumen completo con totales y alertas', () {
      /// Se construye el resumen mensual
      final resumen = construirResumenMensual(
        mes: '2026-10',
        presupuestosPorCategoria: presupuestos,
        movimientos: movimientos,
      );

      /// Se verifica el total presupuestado: 100 + 500 + 300 + 150 = 1050.0
      expect(resumen.totalPresupuestado, equals(1050.0));

      /// Se verifica el total consumido: 120 + 450 + 160 = 730.0
      expect(resumen.totalConsumido, equals(730.0));

      /// Se verifica el restante: 1050 - 730 = 320.0
      expect(resumen.totalRestante, equals(320.0));

      /// Se verifica que Transporte esté listada entre las categorías excedidas
      expect(resumen.categoriasExcedidas, contains('Transporte'));

      /// Se verifica que Comida esté listada entre las categorías en alerta
      expect(resumen.categoriasAlerta, contains('Comida'));
    });
  });
}
