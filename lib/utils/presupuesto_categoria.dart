/// Enumerador que define los 4 posibles estados del presupuesto de una categoría
enum EstadoPresupuesto {
  //un enumerador llamado EstadoPresupuesto, con los valores:
  /// Representa que el usuario aún no ha fijado un monto límite para esta categoría
  sinPresupuesto,

  /// Representa que el consumo va bien y el gasto está por debajo del 80%
  optimo,

  /// Representa una advertencia porque el gasto ya alcanzó o superó el 80% del presupuesto
  alerta,

  /// Representa que el gasto real ya superó el 100% del monto presupuestado
  excedido,
} //fin del enumerador

/// Lista constante de las 5 categorías oficiales disponibles en la aplicación
const List<String> categoriasApp = [
  //una constante categoriasApp es igual a una lista de textos con:
  'Transporte',
  'Comida',
  'Estudios',
  'Ocio',
  'Otros',
];

/// Función que valida el texto ingresado por el usuario al definir un presupuesto
/// Retorna un mensaje de error en texto si es inválido, o null si el valor es correcto
String? validarMontoPresupuesto(String? texto) {
  //una función llamada validarMontoPresupuesto, que recibe un texto opcional texto y devuelve un texto opcional
  /// Se verifica si el texto es nulo o si quitando espacios en blanco queda vacío
  if (texto == null || texto.trim().isEmpty) {
    //si texto es nulo o texto sin espacios está vacío
    /// Se retorna el mensaje de error indicando que no debe estar vacío
    return 'El presupuesto no debe estar vacío'; //retorna "El presupuesto no debe estar vacío"
  }

  /// Intenta convertir el texto limpio a un número decimal double; si contiene letras devuelve null
  final numero = double.tryParse(
    texto.trim(),
  ); //constante numero == a intentar convertir texto sin espacios a decimal

  /// Si el resultado de la conversión es nulo, significa que el usuario escribió letras o símbolos inválidos
  if (numero == null) {
    return 'No se permiten letras, ingresa un número válido'; //retorna "No se permiten letras, ingresa un número válido"
  }

  if (numero <= 0) {
    //si numero es menor o igual a 0
    return 'El presupuesto debe ser mayor a 0'; //retorna "El presupuesto debe ser mayor a 0"
  }

  /// Si pasó todas las validaciones sin fallar, se retorna null indicando que el dato es completamente válido
  return null; //retorna nulo
}

/// Función que calcula la suma total de dinero gastado en una categoría durante un mes específico
double calcularGastoCategoria({
  //una función llamada calcularGastoCategoria, que devuelve un decimal, y recibe:
  required List<Map<String, dynamic>>
  movimientos, //una lista obligatoria movimientos, de mapas de texto a cualquier tipo
  /// Mes a consultar en formato 'YYYY-MM' (por ejemplo: '2026-10')
  required String mes, //un texto obligatorio mes
  /// Nombre de la categoría a consultar (por ejemplo: 'Comida')
  required String categoria,
}) {
  /// Se inicializa el acumulador del monto total en 0.0 decimal
  double total = 0.0; //un decimal total es igual a 0.0

  /// Se recorre cada uno de los movimientos existentes en la lista
  for (final m in movimientos) {
    //para cada movimiento m en movimientos
    /// Se obtiene la fecha como texto seguro (o vacío si es nulo)
    final fechaStr =
        (m['fecha'] ?? '')
            .toString(); //constante fechaStr == a la fecha de m, o vacío si es nulo, como texto

    /// Se obtiene el tipo de movimiento ('gasto' o 'ingreso')
    final tipo =
        (m['tipo'] ?? '')
            .toString(); //constante tipo == al tipo de m, o vacío si es nulo, como texto

    /// Se obtiene el estado del movimiento ('pendiente', 'pagado' o 'cancelado')
    final estado =
        (m['estado'] ?? '')
            .toString(); //constante estado == al estado de m, o vacío si es nulo, como texto

    /// Se obtiene la categoría asignada al movimiento
    final cat =
        (m['categoria'] ?? '')
            .toString(); //constante cat es igual a la categoria de m, o vacío si es nulo, como texto

    /// Se comprueba que la fecha comience con el mes pedido, que sea de tipo 'gasto',
    /// que el estado no sea 'cancelado' y que pertenezca a la categoría solicitada
    if (fechaStr.startsWith(mes) && //si fechaStr empieza con mes, y
        tipo == 'gasto' &&
        estado != 'cancelado' &&
        cat == categoria) {
      /// Se extrae el monto numérico del movimiento y se convierte a double decimal (o 0.0 si es nulo)
      final monto =
          (m['monto'] as num?)?.toDouble() ??
          0.0; //una constante monto == al monto de m como número opcional, convertido a decimal, o 0.0 si es nulo

      /// Se suma este monto al acumulador total de gastos de la categoría
      total += monto; //total == a total más monto
    }
  }

  /// Se devuelve la suma total acumulada de gastos para esa categoría y mes
  return total;
}

/// Función que cuenta cuántas transacciones de gasto válidas se realizaron en una categoría durante un mes
int contarMovimientosCategoria({
  //una función llamada contarMovimientosCategoria, que devuelve un entero, y recibe:
  /// Lista de todos los movimientos registrados
  required List<Map<String, dynamic>>
  movimientos, //una lista obligatoria movimientos, de mapas de texto a cualquier tipo
  /// Mes a consultar en formato 'YYYY-MM'
  required String mes, //un texto obligatorio mes
  /// Nombre de la categoría
  required String categoria, //un texto obligatorio categoria
}) {
  //inicio del cuerpo de la función
  /// Se inicializa el contador de movimientos en cero
  int count = 0; //un entero count es igual a 0

  /// Se recorre cada movimiento de la lista
  for (final m in movimientos) {
    //para cada movimiento m en movimientos
    /// Se extrae la fecha convertida a texto
    final fechaStr =
        (m['fecha'] ?? '')
            .toString(); //una constante fechaStr es igual a la fecha de m, o vacío si es nulo, como texto

    /// Se extrae el tipo de movimiento
    final tipo =
        (m['tipo'] ?? '')
            .toString(); //una constante tipo es igual al tipo de m, o vacío si es nulo, como texto

    /// Se extrae el estado actual
    final estado =
        (m['estado'] ?? '')
            .toString(); //una constante estado es igual al estado de m, o vacío si es nulo, como texto

    /// Se extrae la categoría
    final cat =
        (m['categoria'] ?? '')
            .toString(); //una constante cat es igual a la categoria de m, o vacío si es nulo, como texto

    /// Se verifica que coincida el mes, que sea gasto, que no esté cancelado y sea la categoría
    if (fechaStr.startsWith(mes) && //si fechaStr empieza con mes, y
        tipo == 'gasto' &&
        estado != 'cancelado' &&
        cat == categoria) {
      /// Se incrementa en 1 el contador de transacciones
      count++; //count aumenta en 1
    }
  }

  /// Se devuelve la cantidad total de transacciones encontradas
  return count;
}

/// Función que calcula el porcentaje de consumo dividiendo el gasto real entre el límite presupuestado
double calcularPorcentajeConsumo(double presupuestado, double consumido) {
  //una función llamada calcularPorcentajeConsumo, que recibe un decimal presupuestado y un decimal consumido, y devuelve un decimal
  if (presupuestado <= 0)
    return 0.0; //si presupuestado es menor o igual a 0, retorna 0.0

  /// Se divide el dinero consumido entre el monto presupuestado y se devuelve el resultado decimal
  return consumido /
      presupuestado; //retorna consumido dividido entre presupuestado
} //fin de la función calcularPorcentajeConsumo

/// Función que calcula el saldo disponible restando lo gastado del monto fijado
double calcularSaldoRestante(double presupuestado, double consumido) {
  //una función llamada calcularSaldoRestante, que recibe un decimal presupuestado y un decimal consumido, y devuelve un decimal
  /// Se resta el monto presupuestado menos lo consumido; si da negativo representa exceso de gasto
  return presupuestado - consumido; //retorna presupuestado menos consumido
}

/// Función que evalúa los montos y determina el estado visual del presupuesto (en orden, alerta o excedido)
EstadoPresupuesto obtenerEstadoPresupuesto({
  //una función llamada obtenerEstadoPresupuesto, que devuelve un EstadoPresupuesto, y recibe:
  /// Monto total presupuestado para la categoría
  required double presupuestado, //un decimal obligatorio presupuestado
  /// Monto total gastado en la categoría
  required double consumido, //un decimal obligatorio consumido
}) {
  /// Si el presupuesto fijado es cero o menor a cero, se marca como sin presupuesto
  if (presupuestado <= 0) {
    /// Se retorna el estado sinPresupuesto
    return EstadoPresupuesto
        .sinPresupuesto; //retorna EstadoPresupuesto punto sinPresupuesto
  }

  /// Si lo consumido supera estrictamente el monto presupuestado (más del 100%)
  if (consumido > presupuestado) {
    //si consumido es mayor que presupuestado
    /// Se retorna el estado excedido indicando que se pasó del límite
    return EstadoPresupuesto
        .excedido; //retorna EstadoPresupuesto punto excedido
  }

  if (consumido / presupuestado >= 0.8) {
    //si consumido dividido entre presupuestado es mayor o igual a 0.8
    /// Se retorna el estado alerta advirtiendo que está cerca del tope
    return EstadoPresupuesto.alerta; //retorna EstadoPresupuesto punto alerta
  }

  /// Si no se cumple ninguna de las anteriores, significa que está dentro del rango seguro
  return EstadoPresupuesto.optimo; //retorna EstadoPresupuesto punto optimo
} //fin de la función obtenerEstadoPresupuesto

/// Clase inmutable que contiene toda la información calculada de una categoría individual
class ItemPresupuestoCategoria {
  //una clase llamada ItemPresupuestoCategoria
  /// Nombre de la categoría (ejemplo: 'Comida')
  final String categoria; //un texto constante categoria

  /// Monto de dinero presupuestado fijado por el usuario
  final double presupuestado; //un decimal constante presupuestado

  /// Monto real gastado en el mes
  final double consumido; //un decimal constante consumido

  /// Dinero disponible restante o saldo negativo si se excedió
  final double restante; //un decimal constante restante

  /// Porcentaje de avance de consumo expresado en decimal (ej: 0.75 para 75%)
  final double porcentaje; //un decimal constante porcentaje

  /// Estado calculado (sinPresupuesto, optimo, alerta, excedido)
  final EstadoPresupuesto estado; //un EstadoPresupuesto constante estado

  /// Número de transacciones registradas en esta categoría
  final int cantidadMovimientos; //un entero constante cantidadMovimientos

  /// Constructor con parámetros requeridos
  const ItemPresupuestoCategoria({
    //un constructor constante de ItemPresupuestoCategoria, que recibe:
    required this.categoria, //obligatorio, esta categoria
    required this.presupuestado, //obligatorio, este presupuestado
    required this.consumido, //obligatorio, este consumido
    required this.restante, //obligatorio, este restante
    required this.porcentaje, //obligatorio, este porcentaje
    required this.estado, //obligatorio, este estado
    required this.cantidadMovimientos, //obligatorio, esta cantidadMovimientos
  });

  /// Getter que devuelve verdadero si la categoría tiene un presupuesto mayor a 0
  bool get tienePresupuesto =>
      presupuestado >
      0; //un booleano tienePresupuesto, que devuelve si presupuestado es mayor a 0

  /// Getter que devuelve verdadero si el estado actual es excedido
  bool get estaExcedido =>
      estado ==
      EstadoPresupuesto
          .excedido; //un booleano estaExcedido, que devuelve si estado es igual a excedido

  /// Getter que devuelve verdadero si el estado actual es alerta
  bool get estaEnAlerta =>
      estado ==
      EstadoPresupuesto
          .alerta; //un booleano estaEnAlerta, que devuelve si estado es igual a alerta
}

/// Clase que contiene el resumen consolidado de todo el mes sumando todas las categorías
class ResumenPresupuestoMensual {
  //una clase llamada ResumenPresupuestoMensual
  /// Mes del resumen en formato 'YYYY-MM'
  final String mes; //un texto constante mes

  /// Lista con el detalle procesado de cada una de las 5 categorías
  final List<ItemPresupuestoCategoria>
  items; //una lista constante items, de ItemPresupuestoCategoria

  /// Suma de todos los presupuestos fijados en el mes
  final double totalPresupuestado; //un decimal constante totalPresupuestado

  /// Suma de todos los gastos consumidos en el mes
  final double totalConsumido; //un decimal constante totalConsumido

  /// Dinero restante total disponible en el mes
  final double totalRestante; //un decimal constante totalRestante

  /// Porcentaje general de consumo de todo el mes
  final double porcentajeTotal; //un decimal constante porcentajeTotal

  /// Constructor con parámetros requeridos
  const ResumenPresupuestoMensual({
    //un constructor constante de ResumenPresupuestoMensual, que recibe:
    required this.mes, //obligatorio, este mes
    required this.items, //obligatorio, estos items
    required this.totalPresupuestado, //obligatorio, este totalPresupuestado
    required this.totalConsumido, //obligatorio, este totalConsumido
    required this.totalRestante, //obligatorio, este totalRestante
    required this.porcentajeTotal, //obligatorio, este porcentajeTotal
  });

  /// Getter que filtra y lista solo los nombres de las categorías que superaron su presupuesto
  List<String>
  get categoriasExcedidas => //una lista de textos categoriasExcedidas, que devuelve:
      items
          .where((i) => i.estaExcedido)
          .map((i) => i.categoria)
          .toList(); //de items, donde i está excedido, toma la categoria de i, como lista

  /// Getter que filtra y lista solo los nombres de las categorías que están en alerta (>= 80%)
  List<String>
  get categoriasAlerta => //una lista de textos categoriasAlerta, que devuelve:
      items
          .where((i) => i.estaEnAlerta)
          .map((i) => i.categoria)
          .toList(); //de items, donde i está en alerta, toma la categoria de i, como lista
}

/// Función constructora que procesa los datos y arma el objeto ResumenPresupuestoMensual completo
ResumenPresupuestoMensual construirResumenMensual({
  //una función llamada construirResumenMensual, que devuelve un ResumenPresupuestoMensual, y recibe:
  /// Mes a procesar (ej: '2026-10')
  required String mes, //un texto obligatorio mes
  /// Mapa con los presupuestos asignados a cada categoría { 'Comida': 400.0, ... }
  required Map<String, double>
  presupuestosPorCategoria, //un mapa obligatorio presupuestosPorCategoria, de texto a decimal
  /// Lista de movimientos del usuario leídos de la base de datos
  required List<Map<String, dynamic>>
  movimientos, //una lista obligatoria movimientos, de mapas de texto a cualquier tipo
}) {
  //inicio del cuerpo de la función
  /// Se crea una lista vacía para almacenar el resultado de cada categoría
  final items =
      <
        ItemPresupuestoCategoria
      >[]; //una constante items es igual a una lista vacía de ItemPresupuestoCategoria

  /// Se inicializa la suma de todos los presupuestos en 0.0
  double totalPresupuestado =
      0.0; //un decimal totalPresupuestado es igual a 0.0

  /// Se inicializa la suma de todos los gastos reales en 0.0
  double totalConsumido = 0.0; //un decimal totalConsumido es igual a 0.0

  /// Se itera sobre cada una de las 5 categorías oficiales de la app
  for (final cat in categoriasApp) {
    //para cada categoria cat en categoriasApp
    /// Se obtiene el presupuesto de la categoría o 0.0 si no fue fijado
    final presupuestado =
        presupuestosPorCategoria[cat] ??
        0.0; //una constante presupuestado es igual a presupuestosPorCategoria en cat, o 0.0 si es nulo

    /// Se calcula el gasto real sumando los movimientos de esa categoría en ese mes
    final consumido = calcularGastoCategoria(
      //una constante consumido es igual a calcularGastoCategoria con:
      movimientos: movimientos, //movimientos es igual a movimientos
      mes: mes, //mes es igual a mes
      categoria: cat, //categoria es igual a cat
    ); //fin de la llamada

    /// Se calcula el saldo restante (presupuesto - consumo)
    final restante = calcularSaldoRestante(
      presupuestado,
      consumido,
    ); //una constante restante es igual a calcularSaldoRestante con presupuestado y consumido

    /// Se calcula el porcentaje consumido
    final porcentaje = calcularPorcentajeConsumo(
      presupuestado,
      consumido,
    ); //una constante porcentaje es igual a calcularPorcentajeConsumo con presupuestado y consumido

    /// Se determina el estado de semáforo del presupuesto (óptimo, alerta, excedido o sin presupuesto)
    final estado = obtenerEstadoPresupuesto(
      //una constante estado es igual a obtenerEstadoPresupuesto con:
      presupuestado: presupuestado, //presupuestado es igual a presupuestado
      consumido: consumido, //consumido es igual a consumido
    );

    /// Se cuenta cuántos movimientos de gasto hubo en esa categoría
    final cantidadMovimientos = contarMovimientosCategoria(
      //una constante cantidadMovimientos es igual a contarMovimientosCategoria con:
      movimientos: movimientos, //movimientos es igual a movimientos
      mes: mes, //mes es igual a mes
      categoria: cat, //categoria es igual a cat
    );

    /// Si la categoría tiene presupuesto asignado mayor a cero
    if (presupuestado > 0) {
      //si presupuestado es mayor a 0
      /// Se acumula al total global presupuestado
      totalPresupuestado +=
          presupuestado; //totalPresupuestado es igual a totalPresupuestado más presupuestado
    }

    /// Se acumula el dinero consumido al total global consumido
    totalConsumido +=
        consumido; //totalConsumido es igual a totalConsumido más consumido

    /// Se crea el objeto de la categoría con todos sus cálculos y se agrega a la lista
    items.add(
      //a items, agrega:
      ItemPresupuestoCategoria(
        //un nuevo ItemPresupuestoCategoria con:
        categoria: cat, //categoria es igual a cat
        presupuestado: presupuestado, //presupuestado es igual a presupuestado
        consumido: consumido, //consumido es igual a consumido
        restante: restante, //restante es igual a restante
        porcentaje: porcentaje, //porcentaje es igual a porcentaje
        estado: estado, //estado es igual a estado
        cantidadMovimientos:
            cantidadMovimientos, //cantidadMovimientos es igual a cantidadMovimientos
      ),
    );
  }

  /// Se calcula el saldo total restante restando el consumo total del presupuesto total
  final totalRestante =
      totalPresupuestado -
      totalConsumido; //una constante totalRestante es igual a totalPresupuestado menos totalConsumido

  /// Se calcula el porcentaje total consumido dividiendo gasto total entre presupuesto total (o 0.0 si no hay presupuesto)
  final porcentajeTotal = //una constante porcentajeTotal es igual a:
      totalPresupuestado > 0
          ? (totalConsumido / totalPresupuestado)
          : 0.0; //si totalPresupuestado es mayor a 0, entonces totalConsumido dividido entre totalPresupuestado, si no, 0.0

  return ResumenPresupuestoMensual(
    //retorna un nuevo ResumenPresupuestoMensual con:
    mes: mes, //mes es igual a mes
    items: items, //items es igual a items
    totalPresupuestado:
        totalPresupuestado, //totalPresupuestado es igual a totalPresupuestado
    totalConsumido: totalConsumido, //totalConsumido es igual a totalConsumido
    totalRestante: totalRestante, //totalRestante es igual a totalRestante
    porcentajeTotal:
        porcentajeTotal, //porcentajeTotal es igual a porcentajeTotal
  );
}
