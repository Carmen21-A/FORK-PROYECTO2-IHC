double calcularMontoTotalMovimientos(List<Map<String, dynamic>> movimientos) {
  return movimientos.fold<double>(
    0.0,
    (sum, m) => sum + (m['monto'] as num).toDouble(),
  );
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
