String? validarMontoLimite(String? texto) {
  if (texto == null || texto.trim().isEmpty) {
    return "El límite no puede estar vacío";
  }

  // Si es letra devolvera null
  final numero = double.tryParse(texto);
  if (numero == null) {
    return "No se permite letras, ingresa un numero valido";
  }

  if (numero <= 0) {
    return "El monto tiene que ser mayor a 0";
  }

  return null;
}

bool esLimiteMenorAGasto(double nuevoLimite, double gastoActualMes) {
  return nuevoLimite < gastoActualMes;
}

bool superaLimiteMensual({
  required double gastoActualDelMes,
  required double nuevoGasto,
  required double limite,
}) {
  final nuevoTotal = gastoActualDelMes + nuevoGasto;
  return nuevoTotal > limite;
}

String? getMensajesErrorLimiteMensual({
  required double nuevoMonto,
  required double gastoActual,
  required double limite,
}) {
  final supera = superaLimiteMensual(
    gastoActualDelMes: gastoActual,
    nuevoGasto: nuevoMonto,
    limite: limite,
  );
  final esMenorAGasto = esLimiteMenorAGasto(nuevoMonto, gastoActual);

  if (supera) {
    return 'al editar se excedera el limite mensual de $limite, el gasto actual es $gastoActual';
  } else if (esMenorAGasto) {
    return 'al editar se reduce el limite mensual a $nuevoMonto, no se puede poner limite menor al gasto actual de $gastoActual';
  } else {
    return null;
  }
}

double calcularGastoTotalMes(
  List<Map<String, dynamic>> movimientos,
  String mes,
) {
  // No admite cancelados
  final movimientosMes = movimientos.where(
    (m) =>
        m['fecha'].toString().startsWith(mes) &&
        m['tipo'] == 'gasto' &&
        m['estado'] != 'cancelado',
  );

  return movimientosMes.fold<double>(
    0.0,
    (sum, m) => sum + (m['monto'] as num).toDouble(),
  );
}
