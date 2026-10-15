double calcularMontoTotalMovimientos(List<Map<String, dynamic>> movimientos) {
  double montoTotal = 0.0;
  for (var i = 0; i < movimientos.length; i++) {
    final montoActual = movimientos[i]['monto'] as num;
    montoTotal = montoTotal + montoActual.toDouble();
  }
  return montoTotal;
}

// Suma solo los gastos no cancelados de la lista
double calcularTotalGastos(List<Map<String, dynamic>> movimientos) {
  final gastos = movimientos.where(
    (m) => m['tipo'] == 'gasto' && m['estado'] != 'cancelado',
  );
  return calcularMontoTotalMovimientos(gastos.toList());
}

// Suma solo los ingresos no cancelados de la lista
double calcularTotalIngresos(List<Map<String, dynamic>> movimientos) {
  final ingresos = movimientos.where(
    (m) => m['tipo'] == 'ingreso' && m['estado'] != 'cancelado',
  );
  return calcularMontoTotalMovimientos(ingresos.toList());
}

// Aplica busqueda y filtros sobre una lista de movimientos
List<Map<String, dynamic>> filtrarMovimientos(
  List<Map<String, dynamic>> movimientos, {
  String? texto,
  String? tipo,
  String? categoria,
  String? estado,
  DateTime? desde,
  DateTime? hasta,
}) {
  return movimientos.where((m) {
    // Busqueda por descripcion con coincidencia parcial
    if (texto != null && texto.trim().isNotEmpty) {
      final descripcion = (m['descripcion'] ?? '').toString().toLowerCase();
      if (!descripcion.contains(texto.trim().toLowerCase())) {
        return false;
      }
    }
    if (tipo != null && m['tipo'] != tipo) return false;
    if (categoria != null && m['categoria'] != categoria) return false;
    if (estado != null && m['estado'] != estado) return false;

    if (desde != null || hasta != null) {
      final fecha = DateTime.parse(m['fecha'].toString());
      if (desde != null && fecha.isBefore(desde)) return false;
      if (hasta != null && fecha.isAfter(hasta)) return false;
    }

    return true;
  }).toList();
}
