// Texto legible de un evento del historial
String armarDetalleEvento({
  required String tipo,
  required num monto,
  required String categoria,
  String? descripcion,
}) {
  final tipoTexto = tipo == 'gasto' ? 'Gasto' : 'Ingreso';
  final textoDescripcion =
      (descripcion == null || descripcion.trim().isEmpty)
          ? ''
          : ' · ${descripcion.trim()}';
  return '$tipoTexto $monto Bs · $categoria$textoDescripcion';
}

// Ordena los eventos del mas reciente al mas viejo
List<Map<String, dynamic>> ordenarRecientePrimero(
  List<Map<String, dynamic>> eventos,
) {
  final copia = List<Map<String, dynamic>>.from(eventos);
  copia.sort((a, b) {
    final fechaA = DateTime.tryParse(a['created_at'].toString());
    final fechaB = DateTime.tryParse(b['created_at'].toString());
    if (fechaA == null || fechaB == null) return 0;
    return fechaB.compareTo(fechaA);
  });
  return copia;
}
