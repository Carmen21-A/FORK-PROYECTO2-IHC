/// Enumerador que define los 4 posibles estados del presupuesto de una categoría
enum EstadoPresupuesto {
  /// Representa que el usuario aún no ha fijado un monto límite para esta categoría
  sinPresupuesto,

  /// Representa que el consumo va bien y el gasto está por debajo del 80%
  optimo,

  /// Representa una advertencia porque el gasto ya alcanzó o superó el 80% del presupuesto
  alerta,

  /// Representa que el gasto real ya superó el 100% del monto presupuestado
  excedido,
}

/// Lista constante de las 5 categorías oficiales disponibles en la aplicación
const List<String> categoriasApp = [
  'Transporte',
  'Comida',
  'Estudios',
  'Ocio',
  'Otros',
];

/// Función que valida el texto ingresado por el usuario al definir un presupuesto
/// Retorna un mensaje de error en texto si es inválido, o null si el valor es correcto
String? validarMontoPresupuesto(String? texto) {
  /// Se verifica si el texto es nulo o si quitando espacios en blanco queda vacío
  if (texto == null || texto.trim().isEmpty) {
    /// Se retorna el mensaje de error indicando que no debe estar vacío
    return 'El presupuesto no debe estar vacío';
  }

  /// Intenta convertir el texto limpio a un número decimal double; si contiene letras devuelve null
  final numero = double.tryParse(texto.trim());

  /// Si el resultado de la conversión es nulo, significa que el usuario escribió letras o símbolos inválidos
  if (numero == null) {
    /// Se retorna el mensaje de error solicitando ingresar un número válido
    return 'No se permiten letras, ingresa un número válido';
  }

  /// Se comprueba si el número es cero o un valor negativo menor a cero
  if (numero <= 0) {
    /// Se retorna el mensaje de error exigiendo que el monto sea estrictamente mayor a 0
    return 'El presupuesto debe ser mayor a 0';
  }

  /// Si pasó todas las validaciones sin fallar, se retorna null indicando que el dato es completamente válido
  return null;
}

/// Función que calcula la suma total de dinero gastado en una categoría durante un mes específico
double calcularGastoCategoria({
  /// Lista de todos los movimientos registrados del usuario
  required List<Map<String, dynamic>> movimientos,

  /// Mes a consultar en formato 'YYYY-MM' (por ejemplo: '2026-10')
  required String mes,

  /// Nombre de la categoría a consultar (por ejemplo: 'Comida')
  required String categoria,
}) {
  /// Se inicializa el acumulador del monto total en 0.0 decimal
  double total = 0.0;

  /// Se recorre cada uno de los movimientos existentes en la lista
  for (final m in movimientos) {
    /// Se obtiene la fecha como texto seguro (o vacío si es nulo)
    final fechaStr = (m['fecha'] ?? '').toString();

    /// Se obtiene el tipo de movimiento ('gasto' o 'ingreso')
    final tipo = (m['tipo'] ?? '').toString();

    /// Se obtiene el estado del movimiento ('pendiente', 'pagado' o 'cancelado')
    final estado = (m['estado'] ?? '').toString();

    /// Se obtiene la categoría asignada al movimiento
    final cat = (m['categoria'] ?? '').toString();

    /// Se comprueba que la fecha comience con el mes pedido, que sea de tipo 'gasto',
    /// que el estado no sea 'cancelado' y que pertenezca a la categoría solicitada
    if (fechaStr.startsWith(mes) &&
        tipo == 'gasto' &&
        estado != 'cancelado' &&
        cat == categoria) {
      /// Se extrae el monto numérico del movimiento y se convierte a double decimal (o 0.0 si es nulo)
      final monto = (m['monto'] as num?)?.toDouble() ?? 0.0;

      /// Se suma este monto al acumulador total de gastos de la categoría
      total += monto;
    }
  }

  /// Se devuelve la suma total acumulada de gastos para esa categoría y mes
  return total;
}

/// Función que cuenta cuántas transacciones de gasto válidas se realizaron en una categoría durante un mes
int contarMovimientosCategoria({
  /// Lista de todos los movimientos registrados
  required List<Map<String, dynamic>> movimientos,

  /// Mes a consultar en formato 'YYYY-MM'
  required String mes,

  /// Nombre de la categoría
  required String categoria,
}) {
  /// Se inicializa el contador de movimientos en cero
  int count = 0;

  /// Se recorre cada movimiento de la lista
  for (final m in movimientos) {
    /// Se extrae la fecha convertida a texto
    final fechaStr = (m['fecha'] ?? '').toString();

    /// Se extrae el tipo de movimiento
    final tipo = (m['tipo'] ?? '').toString();

    /// Se extrae el estado actual
    final estado = (m['estado'] ?? '').toString();

    /// Se extrae la categoría
    final cat = (m['categoria'] ?? '').toString();

    /// Se verifica que coincida el mes, que sea gasto, que no esté cancelado y sea la categoría
    if (fechaStr.startsWith(mes) &&
        tipo == 'gasto' &&
        estado != 'cancelado' &&
        cat == categoria) {
      /// Se incrementa en 1 el contador de transacciones
      count++;
    }
  }

  /// Se devuelve la cantidad total de transacciones encontradas
  return count;
}

/// Función que calcula el porcentaje de consumo dividiendo el gasto real entre el límite presupuestado
double calcularPorcentajeConsumo(double presupuestado, double consumido) {
  /// Si el presupuesto es menor o igual a cero, no se puede dividir por cero, por lo que se retorna 0.0
  if (presupuestado <= 0) return 0.0;

  /// Se divide el dinero consumido entre el monto presupuestado y se devuelve el resultado decimal
  return consumido / presupuestado;
}

/// Función que calcula el saldo disponible restando lo gastado del monto fijado
double calcularSaldoRestante(double presupuestado, double consumido) {
  /// Se resta el monto presupuestado menos lo consumido; si da negativo representa exceso de gasto
  return presupuestado - consumido;
}

/// Función que evalúa los montos y determina el estado visual del presupuesto (en orden, alerta o excedido)
EstadoPresupuesto obtenerEstadoPresupuesto({
  /// Monto total presupuestado para la categoría
  required double presupuestado,

  /// Monto total gastado en la categoría
  required double consumido,
}) {
  /// Si el presupuesto fijado es cero o menor a cero, se marca como sin presupuesto
  if (presupuestado <= 0) {
    /// Se retorna el estado sinPresupuesto
    return EstadoPresupuesto.sinPresupuesto;
  }

  /// Si lo consumido supera estrictamente el monto presupuestado (más del 100%)
  if (consumido > presupuestado) {
    /// Se retorna el estado excedido indicando que se pasó del límite
    return EstadoPresupuesto.excedido;
  }

  /// Si la proporción consumido / presupuestado es igual o mayor a 0.8 (es decir, 80% o más)
  if (consumido / presupuestado >= 0.8) {
    /// Se retorna el estado alerta advirtiendo que está cerca del tope
    return EstadoPresupuesto.alerta;
  }

  /// Si no se cumple ninguna de las anteriores, significa que está dentro del rango seguro
  return EstadoPresupuesto.optimo;
}

/// Clase inmutable que contiene toda la información calculada de una categoría individual
class ItemPresupuestoCategoria {
  /// Nombre de la categoría (ejemplo: 'Comida')
  final String categoria;

  /// Monto de dinero presupuestado fijado por el usuario
  final double presupuestado;

  /// Monto real gastado en el mes
  final double consumido;

  /// Dinero disponible restante o saldo negativo si se excedió
  final double restante;

  /// Porcentaje de avance de consumo expresado en decimal (ej: 0.75 para 75%)
  final double porcentaje;

  /// Estado calculado (sinPresupuesto, optimo, alerta, excedido)
  final EstadoPresupuesto estado;

  /// Número de transacciones registradas en esta categoría
  final int cantidadMovimientos;

  /// Constructor con parámetros requeridos
  const ItemPresupuestoCategoria({
    required this.categoria,
    required this.presupuestado,
    required this.consumido,
    required this.restante,
    required this.porcentaje,
    required this.estado,
    required this.cantidadMovimientos,
  });

  /// Getter que devuelve verdadero si la categoría tiene un presupuesto mayor a 0
  bool get tienePresupuesto => presupuestado > 0;

  /// Getter que devuelve verdadero si el estado actual es excedido
  bool get estaExcedido => estado == EstadoPresupuesto.excedido;

  /// Getter que devuelve verdadero si el estado actual es alerta
  bool get estaEnAlerta => estado == EstadoPresupuesto.alerta;
}

/// Clase que contiene el resumen consolidado de todo el mes sumando todas las categorías
class ResumenPresupuestoMensual {
  /// Mes del resumen en formato 'YYYY-MM'
  final String mes;

  /// Lista con el detalle procesado de cada una de las 5 categorías
  final List<ItemPresupuestoCategoria> items;

  /// Suma de todos los presupuestos fijados en el mes
  final double totalPresupuestado;

  /// Suma de todos los gastos consumidos en el mes
  final double totalConsumido;

  /// Dinero restante total disponible en el mes
  final double totalRestante;

  /// Porcentaje general de consumo de todo el mes
  final double porcentajeTotal;

  /// Constructor con parámetros requeridos
  const ResumenPresupuestoMensual({
    required this.mes,
    required this.items,
    required this.totalPresupuestado,
    required this.totalConsumido,
    required this.totalRestante,
    required this.porcentajeTotal,
  });

  /// Getter que filtra y lista solo los nombres de las categorías que superaron su presupuesto
  List<String> get categoriasExcedidas =>
      items.where((i) => i.estaExcedido).map((i) => i.categoria).toList();

  /// Getter que filtra y lista solo los nombres de las categorías que están en alerta (>= 80%)
  List<String> get categoriasAlerta =>
      items.where((i) => i.estaEnAlerta).map((i) => i.categoria).toList();
}

/// Función constructora que procesa los datos y arma el objeto ResumenPresupuestoMensual completo
ResumenPresupuestoMensual construirResumenMensual({
  /// Mes a procesar (ej: '2026-10')
  required String mes,

  /// Mapa con los presupuestos asignados a cada categoría { 'Comida': 400.0, ... }
  required Map<String, double> presupuestosPorCategoria,

  /// Lista de movimientos del usuario leídos de la base de datos
  required List<Map<String, dynamic>> movimientos,
}) {
  /// Se crea una lista vacía para almacenar el resultado de cada categoría
  final items = <ItemPresupuestoCategoria>[];

  /// Se inicializa la suma de todos los presupuestos en 0.0
  double totalPresupuestado = 0.0;

  /// Se inicializa la suma de todos los gastos reales en 0.0
  double totalConsumido = 0.0;

  /// Se itera sobre cada una de las 5 categorías oficiales de la app
  for (final cat in categoriasApp) {
    /// Se obtiene el presupuesto de la categoría o 0.0 si no fue fijado
    final presupuestado = presupuestosPorCategoria[cat] ?? 0.0;

    /// Se calcula el gasto real sumando los movimientos de esa categoría en ese mes
    final consumido = calcularGastoCategoria(
      movimientos: movimientos,
      mes: mes,
      categoria: cat,
    );

    /// Se calcula el saldo restante (presupuesto - consumo)
    final restante = calcularSaldoRestante(presupuestado, consumido);

    /// Se calcula el porcentaje consumido
    final porcentaje = calcularPorcentajeConsumo(presupuestado, consumido);

    /// Se determina el estado de semáforo del presupuesto (óptimo, alerta, excedido o sin presupuesto)
    final estado = obtenerEstadoPresupuesto(
      presupuestado: presupuestado,
      consumido: consumido,
    );

    /// Se cuenta cuántos movimientos de gasto hubo en esa categoría
    final cantidadMovimientos = contarMovimientosCategoria(
      movimientos: movimientos,
      mes: mes,
      categoria: cat,
    );

    /// Si la categoría tiene presupuesto asignado mayor a cero
    if (presupuestado > 0) {
      /// Se acumula al total global presupuestado
      totalPresupuestado += presupuestado;
    }

    /// Se acumula el dinero consumido al total global consumido
    totalConsumido += consumido;

    /// Se crea el objeto de la categoría con todos sus cálculos y se agrega a la lista
    items.add(
      ItemPresupuestoCategoria(
        categoria: cat,
        presupuestado: presupuestado,
        consumido: consumido,
        restante: restante,
        porcentaje: porcentaje,
        estado: estado,
        cantidadMovimientos: cantidadMovimientos,
      ),
    );
  }

  /// Se calcula el saldo total restante restando el consumo total del presupuesto total
  final totalRestante = totalPresupuestado - totalConsumido;

  /// Se calcula el porcentaje total consumido dividiendo gasto total entre presupuesto total (o 0.0 si no hay presupuesto)
  final porcentajeTotal =
      totalPresupuestado > 0 ? (totalConsumido / totalPresupuestado) : 0.0;

  /// Se retorna la instancia completa de ResumenPresupuestoMensual con todos los valores procesados
  return ResumenPresupuestoMensual(
    mes: mes,
    items: items,
    totalPresupuestado: totalPresupuestado,
    totalConsumido: totalConsumido,
    totalRestante: totalRestante,
    porcentajeTotal: porcentajeTotal,
  );
}
