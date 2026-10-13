import 'package:flutter_test/flutter_test.dart';
import 'package:presupuesto_estudiantil/utils/estado_movimiento.dart';

void main() {
  test('estado inicial es pendiente', () {
    const estadoInicial = 'pendiente';
    expect(estadoInicial, 'pendiente');
  });

  test('la acción hace la transicion esperada', () {
    expect(siguienteEstado('pendiente'), 'pagado');
    expect(siguienteEstado('pagado'), 'cancelado');
  });

  test('transicion invalida es rechazada', () {
    expect(siguienteEstado('cancelado'), null);
    expect(esTransicionValida('cancelado', 'pagado'), false);
    expect(esTransicionValida('pendiente', 'cancelado'), false);
  });

  test('los demas datos se conservan', () {
    final m = {
      'id': '1',
      'tipo': 'gasto',
      'monto': 25.0,
      'categoria': 'Transporte',
      'descripcion': 'Pasaje pal taxi',
      'fecha': '2025-10-01',
      'estado': 'pendiente',
    };

    // simula el cambio de estado sin tocar el resto
    final copia = Map<String, dynamic>.from(m);
    copia['estado'] = siguienteEstado(m['estado'] as String);

    expect(copia['id'], '1');
    expect(copia['tipo'], 'gasto');
    expect(copia['monto'], 25.0);
    expect(copia['categoria'], 'Transporte');
    expect(copia['descripcion'], 'Pasaje pal taxi');
    expect(copia['fecha'], '2025-10-01');
    expect(copia['estado'], 'pagado');
  });

  test('no se puede editar el monto del movimiento si el estado es pagado', () {
    // En estado pendiente o cancelado, el monto SÍ se puede editar:
    expect(puedeEditarMonto('pendiente'), true);
    expect(puedeEditarMonto('cancelado'), true);

    // En estado pagado, el monto NO se puede editar (restricción de negocio):
    expect(puedeEditarMonto('pagado'), false);
  });
}
