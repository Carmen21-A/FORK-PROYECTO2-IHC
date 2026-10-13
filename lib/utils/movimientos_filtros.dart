double calcularMontoTotalMovimientos(List<Map<String, dynamic>> movimientos) {
  return movimientos.fold<double>(
    0.0,
    (sum, m) => sum + (m['monto'] as num).toDouble(),
  );
}
