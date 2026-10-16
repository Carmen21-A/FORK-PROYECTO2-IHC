import 'package:flutter/material.dart';
import 'package:presupuesto_estudiantil/design_system/color_styles.dart';
import 'package:presupuesto_estudiantil/utils/estado_movimiento.dart';
import 'package:presupuesto_estudiantil/widgets/app_drawer.dart';
import '../services/movements_service.dart';
import 'package:presupuesto_estudiantil/utils/limite_mensual.dart';
import 'package:presupuesto_estudiantil/utils/movimientos_filtros.dart';
import 'package:presupuesto_estudiantil/services/limites_service.dart';

class MovementsScreen extends StatefulWidget {
  const MovementsScreen({super.key});

  @override
  State<MovementsScreen> createState() => _MovementsScreenState();
}

class _MovementsScreenState extends State<MovementsScreen> {
  final _formularioId = GlobalKey<FormState>();
  final _montoController = TextEditingController();
  final _descripcionController = TextEditingController();
  final _busquedaController = TextEditingController();
  final _service = MovementsService();
  final _limitesService = LimitesService();

  String _tipo = 'gasto';
  String _categoria = 'Transporte';
  DateTime _fecha = DateTime.now();
  List<Map<String, dynamic>> _movimientos = [];
  List<Map<String, dynamic>> _movimientosFiltrados = [];
  String? _editingId;
  String? _editingState;
  double? _limiteMensual;
  bool _guardando = false;
  double? _limiteMesForm;

  String _filtroTipo = 'todos';
  String _filtroCategoria = 'todos';
  String _filtroPeriodo = 'todos';
  String _filtroEstado = 'todos';
  DateTime? _rangoDesde;
  DateTime? _rangoHasta;

  @override
  void initState() {
    super.initState();
    _load();
    _cargarLimiteForm();
  }

  @override
  void dispose() {
    _montoController.dispose();
    _descripcionController.dispose();
    _busquedaController.dispose();
    super.dispose();
  }

  // Carga los movimientos (todos y filtrados) desde Supabase, y el limite
  Future<void> _load() async {
    final data = await _service.getAll();
    final filtrados = await _service.buscarConFiltros(
      texto: _busquedaController.text,
      tipo: _filtroTipo == 'todos' ? null : _filtroTipo,
      categoria: _filtroCategoria == 'todos' ? null : _filtroCategoria,
      estado: _filtroEstado == 'todos' ? null : _filtroEstado,
      desde: _periodoDesde(),
      hasta: _periodoHasta(),
    );
    final mesActual =
        '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}';
    final limite = await _limitesService.getLimit(mesActual);
    if (mounted) {
      setState(() {
        _movimientos = data;
        _movimientosFiltrados = filtrados;
        _limiteMensual = limite;
      });
    }
  }

  // Carga el limite del mes de la fecha del formulario (para la validacion en vivo)
  Future<void> _cargarLimiteForm() async {
    final mes = '${_fecha.year}-${_fecha.month.toString().padLeft(2, '0')}';
    final limite = await _limitesService.getLimit(mes);
    if (mounted) {
      setState(() => _limiteMesForm = limite);
    }
  }

  // Aviso en vivo cuando el monto supera el limite disponible del mes
  String? _avisoMontoExcedido() {
    if (_tipo != 'gasto') return null;
    final limite = _limiteMesForm;
    if (limite == null) return null;

    final monto = double.tryParse(_montoController.text);
    if (monto == null || monto <= 0) return null;

    final mes = '${_fecha.year}-${_fecha.month.toString().padLeft(2, '0')}';
    var gastoActual = calcularGastoTotalMes(_movimientos, mes);

    // Si se esta editando, no se cuenta dos veces el monto anterior
    if (_editingId != null) {
      final movViejo = _movimientos.firstWhere((m) => m['id'] == _editingId);
      if (movViejo['tipo'] == 'gasto' && movViejo['estado'] != 'cancelado') {
        gastoActual -= (movViejo['monto'] as num).toDouble();
      }
    }

    final disponible = limite - gastoActual;
    if (monto > disponible) {
      return 'Supera tu límite mensual. Disponible: $disponible Bs de $limite Bs.';
    }
    return null;
  }

  // Muestra el limite que esta disponible en el formulario de gasto
  Widget _indicadorLimiteForm() {
    if (_tipo != 'gasto') {
      return const SizedBox.shrink();
    }

    final limite = _limiteMesForm ?? _limiteMensual;
    if (limite == null) {
      return const SizedBox.shrink();
    }

    final mes = '${_fecha.year}-${_fecha.month.toString().padLeft(2, '0')}';
    var gastoActual = calcularGastoTotalMes(_movimientos, mes);

    if (_editingId != null) {
      final movViejo = _movimientos.firstWhere((m) => m['id'] == _editingId);
      if (movViejo['tipo'] == 'gasto' && movViejo['estado'] != 'cancelado') {
        gastoActual -= (movViejo['monto'] as num).toDouble();
      }
    }

    final disponible = limite - gastoActual;
    final disponibleTexto = disponible >= 0 ? '$disponible Bs' : '0 Bs';

    return Padding(
      padding: const EdgeInsets.only(top: 6, bottom: 4),
      child: Text(
        'Límite disponible: $disponibleTexto de $limite Bs',
        style: const TextStyle(
          fontSize: 13,
          color: Colors.black,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  // Fecha inicial del periodo seleccionado
  DateTime? _periodoDesde() {
    final hoy = DateTime.now();
    if (_filtroPeriodo == 'este mes') {
      return DateTime(hoy.year, hoy.month, 1);
    }
    if (_filtroPeriodo == 'mes pasado') {
      return DateTime(hoy.year, hoy.month - 1, 1);
    }
    if (_filtroPeriodo == 'rango') {
      return _rangoDesde;
    }
    return null;
  }

  // Fecha final del periodo seleccionado
  DateTime? _periodoHasta() {
    final hoy = DateTime.now();
    if (_filtroPeriodo == 'este mes') {
      return DateTime(hoy.year, hoy.month + 1, 0);
    }
    if (_filtroPeriodo == 'mes pasado') {
      return DateTime(hoy.year, hoy.month, 0);
    }
    if (_filtroPeriodo == 'rango') {
      return _rangoHasta;
    }
    return null;
  }

  Future<void> _cambiarPeriodo(String valor) async {
    if (valor != 'rango') {
      setState(() => _filtroPeriodo = valor);
      _load();
      return;
    }

    final rango = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (rango == null) return;

    setState(() {
      _filtroPeriodo = 'rango';
      _rangoDesde = rango.start;
      _rangoHasta = rango.end;
    });
    _load();
  }

  Widget _dropdownFiltro(
    String etiqueta,
    String valorActual,
    List<String> opciones,
    Function(String) alCambiar,
  ) {
    return DropdownButton<String>(
      value: valorActual,
      hint: Text(etiqueta),
      items:
          opciones
              .map((o) => DropdownMenuItem(value: o, child: Text(o)))
              .toList(),
      onChanged: (v) {
        if (v == null) return;
        alCambiar(v);
      },
    );
  }

  // Chips de los filtros activos, con opcion de quitarlos
  List<Widget> _chipsFiltros() {
    final chips = <Widget>[];

    if (_busquedaController.text.trim().isNotEmpty) {
      chips.add(
        Chip(
          label: Text('Buscar: ${_busquedaController.text.trim()}'),
          onDeleted: () {
            _busquedaController.clear();
            _load();
          },
        ),
      );
    }
    if (_filtroTipo != 'todos') {
      chips.add(
        Chip(
          label: Text('Tipo: $_filtroTipo'),
          onDeleted: () {
            setState(() => _filtroTipo = 'todos');
            _load();
          },
        ),
      );
    }
    if (_filtroCategoria != 'todos') {
      chips.add(
        Chip(
          label: Text('Categoría: $_filtroCategoria'),
          onDeleted: () {
            setState(() => _filtroCategoria = 'todos');
            _load();
          },
        ),
      );
    }
    if (_filtroPeriodo != 'todos') {
      chips.add(
        Chip(
          label: Text(
            'Periodo: ${_filtroPeriodo == 'rango' ? '${_fechaCorta(_rangoDesde)} - ${_fechaCorta(_rangoHasta)}' : _filtroPeriodo}',
          ),

          onDeleted: () {
            setState(() {
              _filtroPeriodo = 'todos';
              _rangoDesde = null;
              _rangoHasta = null;
            });
            _load();
          },
        ),
      );
    }
    if (_filtroEstado != 'todos') {
      chips.add(
        Chip(
          label: Text('Estado: $_filtroEstado'),
          onDeleted: () {
            setState(() => _filtroEstado = 'todos');
            _load();
          },
        ),
      );
    }

    return chips;
  }

  Widget _panelFiltros() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _busquedaController,
                  textInputAction:
                      TextInputAction.search, // add buton en teclado android
                  onSubmitted: (_) => _load(),
                  decoration: InputDecoration(
                    hintText: 'Buscar por descripción',
                  ),
                ),
              ),
              ElevatedButton(onPressed: _load, child: const Text('Buscar')),
            ],
          ),

          Wrap(
            spacing: 16,
            runSpacing: 4,
            children: [
              _dropdownFiltro(
                'Tipo',
                _filtroTipo,
                ['todos', 'gasto', 'ingreso'],
                (v) {
                  setState(() => _filtroTipo = v);
                  _load();
                },
              ),
              _dropdownFiltro(
                'Categoría',
                _filtroCategoria,
                ['todos', 'Transporte', 'Comida', 'Estudios', 'Ocio', 'Otros'],
                (v) {
                  setState(() => _filtroCategoria = v);
                  _load();
                },
              ),
              _dropdownFiltro('Periodo', _filtroPeriodo, [
                'todos',
                'este mes',
                'mes pasado',
                'rango',
              ], (v) => _cambiarPeriodo(v)),
              _dropdownFiltro(
                'Estado',
                _filtroEstado,
                ['todos', 'pendiente', 'pagado', 'cancelado'],
                (v) {
                  setState(() => _filtroEstado = v);
                  _load();
                },
              ),
            ],
          ),
          Wrap(spacing: 8, children: _chipsFiltros()),
          Text(
            'Total gastos: ${calcularTotalGastos(_movimientosFiltrados)} Bs · Total ingresos: ${calcularTotalIngresos(_movimientosFiltrados)} Bs',
          ),
        ],
      ),
    );
  }

  Widget _tarjetaResumenLimite() {
    final mesActual =
        '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}';
    final gastoActual = calcularGastoTotalMes(_movimientos, mesActual);
    final limite = _limiteMensual;
    final disponible = limite != null ? (limite - gastoActual) : null;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Gastado: $gastoActual Bs / Límite: ${limite != null ? "$limite Bs" : "Sin definir"}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    limite != null
                        ? 'Disponible: ${disponible! >= 0 ? disponible : 0} Bs'
                        : 'Define un limite para controlar tus gastos',
                    style: TextStyle(
                      color:
                          (disponible != null && disponible <= 0)
                              ? ColorStyles.errorDefault
                              : ColorStyles.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            OutlinedButton(
              onPressed: _dialogoCambiarLimite,
              child: Text(limite == null ? 'Definir' : 'Cambiar'),
            ),
          ],
        ),
      ),
    );
  }

  // Esto sirve para cambiar el limite mensual
  Future<void> _dialogoCambiarLimite() async {
    final controller = TextEditingController(
      text: _limiteMensual != null ? _limiteMensual.toString() : '',
    );
    final formularioId = GlobalKey<FormState>();
    final mesActual =
        '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}';
    final gastoActual = calcularGastoTotalMes(_movimientos, mesActual);

    var guardando = false;
    await showDialog(
      context: context,
      builder:
          (ctx) => StatefulBuilder(
            builder:
                (ctx, setDialogState) => AlertDialog(
                  title: const Text('Límite mensual de gastos'),
                  content: Form(
                    key: formularioId,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('Gasto actual del mes: $gastoActual Bs'),
                        TextFormField(
                          controller: controller,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Nuevo límite',
                            hintText: 'Ej: 500',
                          ),
                          validator: (monto) {
                            // Que no este vacio, sin letras y solo numeros
                            final errorFormato = validarMontoLimite(monto);
                            if (errorFormato != null) return errorFormato;

                            // Verifica que no sea menor a lo ya gastado
                            final n = double.parse(monto!);
                            if (esLimiteMenorAGasto(n, gastoActual)) {
                              return 'No puede ser menor a lo ya gastado "$gastoActual Bs"';
                            }
                            return null;
                          },
                        ),
                      ],
                    ),
                  ),
                  actions: [
                    OutlinedButton(
                      onPressed: guardando ? null : () => Navigator.pop(ctx),
                      child: const Text('Cancelar'),
                    ),
                    ElevatedButton(
                      onPressed:
                          guardando
                              ? null
                              : () async {
                                if (!formularioId.currentState!.validate()) {
                                  return;
                                }
                                setDialogState(() => guardando = true);
                                final nuevoLimite = double.parse(
                                  controller.text,
                                );
                                await _limitesService.saveMonthLimit(
                                  mes: mesActual,
                                  limite: nuevoLimite,
                                );
                                if (ctx.mounted) {
                                  Navigator.pop(ctx);
                                  _load();
                                  _cargarLimiteForm();
                                }
                              },
                      child:
                          guardando
                              ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                              : const Text('Guardar'),
                    ),
                  ],
                ),
          ),
    );
  }

  Future<bool> _validarSiExcedioLimiteMensual(double monto) async {
    if (_tipo != 'gasto') return false;

    final mes = '${_fecha.year}-${_fecha.month.toString().padLeft(2, '0')}';
    final limite = await _limitesService.getLimit(mes);
    if (limite == null) return false;

    var gastoActual = calcularGastoTotalMes(_movimientos, mes);

    // Si se esta editando, no se cuenta dos veces el monto anterior
    if (_editingId != null) {
      final movViejo = _movimientos.firstWhere((m) => m['id'] == _editingId);
      if (movViejo['tipo'] == 'gasto' && movViejo['estado'] != 'cancelado') {
        gastoActual -= (movViejo['monto'] as num).toDouble();
      }
    }

    if (superaLimiteMensual(
      gastoActualDelMes: gastoActual,
      nuevoGasto: monto,
      limite: limite,
    )) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: ColorStyles.errorDefault,
            content: Text(
              'No se puede registrar, porque supera tu límite mensual de $limite Bs (llevas gastando $gastoActual Bs)',
            ),
          ),
        );
      }
      return true; // Se excedio
    }

    return false; // No se excedio
  }

  Future<void> _save() async {
    if (_guardando) return;
    if (!_formularioId.currentState!.validate()) return;
    final monto = double.tryParse(_montoController.text) ?? 0;

    final excede = await _validarSiExcedioLimiteMensual(monto);
    if (excede) return;

    setState(() => _guardando = true);
    try {
      if (_editingId == null) {
        //Se esta creando un uno
        await _service.create(
          tipo: _tipo,
          monto: monto,
          categoria: _categoria,
          fecha: _fecha,
          descripcion: _descripcionController.text.trim(),
        );
      } else {
        // Se esta editando uno movimiento existente
        await _service.update(
          id: _editingId!,
          tipo: _tipo,
          monto: monto,
          categoria: _categoria,
          fecha: _fecha,
          descripcion: _descripcionController.text.trim(),
        );
        _editingId = null;
        _editingState = null;
      }

      if (mounted) {
        // Se vuevle a cargar la lista
        _load();
      }
    } catch (_) {
    } finally {
      if (mounted) {
        setState(() => _guardando = false);
      }
    }

    _montoController.text = "";
    _descripcionController.text = "";
  }

  Future<void> _delete(String id) async {
    try {
      await _service.delete(id);
      if (mounted) {
        _load();
      }
    } catch (_) {}
  }

  Future<void> _prepareEdition(Map<String, dynamic> m) async {
    setState(() {
      _editingId = m['id'] as String;
      _montoController.text = m['monto'].toString();
      _descripcionController.text = (m['descripcion'] ?? '').toString();
      _tipo = m['tipo'] as String;
      _categoria = m['categoria'] as String;
      _fecha = DateTime.parse(m['fecha'] as String);
      _editingState = m['estado'] as String;
    });
    _cargarLimiteForm();
  }

  Future<void> _confirmDeletion(String id) async {
    final responder = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Confirma que quieres eliminar este movimiento'),
            content: const Text(
              '¿Estás seguro que quieres eliminar este movimiento?',
            ),
            actions: [
              OutlinedButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancelar'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Eliminar'),
              ),
            ],
          ),
    );

    // Si se elige Eliminar, se procede con el borrado en Supabase
    if (responder == true) {
      _delete(id);
    }
  }

  final meses = [
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
  ];

  String _fechaTexto(String iso) {
    final d = DateTime.parse(iso);
    return '${d.day} de ${meses[d.month - 1]}';
  }

  String _fechaCorta(DateTime? fecha) {
    if (fecha == null) return '?';
    return '${fecha.day}/${fecha.month}/${fecha.year}';
  }

  Future<void> _cambiarEstado(Map<String, dynamic> m) async {
    final actual = m['estado'];
    final siguiente = siguienteEstado(actual);
    if (siguiente == null) return;

    // Cancelar es irreversible: pedimos confirmacion antes
    if (siguiente == 'cancelado') {
      final confirmar = await showDialog<bool>(
        context: context,
        builder:
            (context) => AlertDialog(
              title: const Text('Confirmar cancelacion'),
              content: const Text(
                '¿Seguro que quieres cancelar este movimiento? Esta acción no se puede deshacer.',
              ),
              actions: [
                OutlinedButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Volver'),
                ),
                ElevatedButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: const Text('Cancelar movimiento'),
                ),
              ],
            ),
      );
      if (confirmar != true) return;
    }

    await _service.cambiarEstado(m['id'], siguiente);
    _load();
  }

  final Map<String, Color> _estadoXColor = {
    'pendiente': Colors.blue,
    'pagado': Colors.green,
    'cancelado': Colors.red,
  };

  Color escoger(String entrada) {
    return _estadoXColor[entrada]!;
  }

  void _mostrarDialogoAyuda() {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.help_outline, color: Colors.blue),
                SizedBox(width: 8),
                Text('Ayuda'),
              ],
            ),
            content: const SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Límite:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'Este es el monto máximo que tienes planeado gastar en el mes, si intentaras registrar un gasto que supere tu límite, la app lo bloqueará para cuidar tu presupuesto.',
                  ),
                  Text(
                    'Gastos e Ingresos:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '• Gasto: es el dinero que pagas o usas (transporte, comida, estudios, etc.), cada gasto que anotas se descuenta de tu límite del mes.\n'
                    '• Ingreso: dinero que recibes (mesada, sueldo, etc.) y no consume tu límite.',
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Estados de los movimientos:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    '• Pendiente: movimiento registrado.\n'
                    '• Pagado: dinero ya desembolsado (su monto no se puede cambiar).\n'
                    '• Cancelado: movimiento anulado.',
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Entendido'),
              ),
            ],
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final avisoMonto = _avisoMontoExcedido();
    return Scaffold(
      drawer: const AppDrawer(),
      appBar: AppBar(
        title: const Text('Movimientos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            tooltip: 'Ayuda',
            onPressed: _mostrarDialogoAyuda,
          ),
        ],
      ),

      body: Column(
        children: [
          _tarjetaResumenLimite(),
          _panelFiltros(),
          Expanded(
            child: ListView(
              children: [
                if (_movimientosFiltrados.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Text(
                      'No hay movimientos que coincidan con la búsqueda',
                      textAlign: TextAlign.center,
                    ),
                  ),
                ..._movimientosFiltrados.map((m) {
                  final tipo = m['tipo'] as String;
                  final montoNum = m['monto'] as num;
                  final montoTexto =
                      montoNum == montoNum.toInt()
                          ? montoNum.toInt().toString()
                          : montoNum.toString();
                  final categoria = m['categoria'];
                  final descripcion = (m['descripcion'] ?? '').toString();
                  final fecha = _fechaTexto(m['fecha'] as String);
                  final esGasto = tipo == 'gasto';
                  final colorMonto =
                      esGasto ? ColorStyles.errorDark : ColorStyles.successDark;

                  return ListTile(
                    title: Text(
                      '${esGasto ? '-' : '+'} $montoTexto Bs',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: colorMonto,
                      ),
                    ),
                    subtitle: Text(
                      '$categoria · $fecha${descripcion.isEmpty ? '' : ' · $descripcion'}',
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        OutlinedButton(
                          onPressed: () => _cambiarEstado(m),
                          style: ButtonStyle(
                            foregroundColor: WidgetStatePropertyAll<Color>(
                              escoger(m['estado']),
                            ),
                            side: WidgetStatePropertyAll(
                              BorderSide(
                                color: escoger(m['estado']),
                                width: 1.5,
                              ),
                            ),
                          ),
                          child: Text('${m['estado']}'),
                        ),
                        PopupMenuButton<String>(
                          icon: const Icon(Icons.more_vert),
                          tooltip: 'Opciones',
                          onSelected: (opcion) {
                            if (opcion == 'editar') {
                              _prepareEdition(m);
                            } else if (opcion == 'eliminar') {
                              _confirmDeletion(m['id'] as String);
                            }
                          },
                          itemBuilder:
                              (context) => [
                                const PopupMenuItem(
                                  value: 'editar',
                                  child: Row(
                                    children: [
                                      Icon(Icons.edit_outlined, size: 20),
                                      SizedBox(width: 8),
                                      Text('Editar'),
                                    ],
                                  ),
                                ),
                                const PopupMenuItem(
                                  value: 'eliminar',
                                  child: Row(
                                    children: [
                                      Icon(
                                        Icons.delete_outline,
                                        color: Colors.red,
                                        size: 20,
                                      ),
                                      SizedBox(width: 8),
                                      Text(
                                        'Eliminar',
                                        style: TextStyle(color: Colors.red),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                        ),
                      ],
                    ),
                  );
                }),
                Form(
                  key: _formularioId,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: SizedBox(
                      width: double.infinity,
                      child: Column(
                        children: [
                          // Si _editingId NO es nulo, mostramos este aviso:
                          if (_editingId != null) ...[
                            Container(
                              padding: const EdgeInsets.all(8),
                              child: Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text(
                                    'Edita este movimiento',
                                    style: TextStyle(
                                      color: Colors.orange,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),

                                  OutlinedButton(
                                    onPressed: () {
                                      setState(() {
                                        _editingId = null;
                                        _editingState = null;
                                        _montoController.clear();
                                        _descripcionController.clear();
                                      });
                                    },
                                    child: const Text('Cancelar'),
                                  ),
                                ],
                              ),
                            ),
                          ],

                          SizedBox(
                            width: double.infinity,
                            child: Wrap(
                              direction: Axis.horizontal,
                              crossAxisAlignment: WrapCrossAlignment.center,
                              alignment: WrapAlignment.spaceAround,
                              children: [
                                DropdownButton<String>(
                                  value: _tipo,
                                  items: [
                                    DropdownMenuItem(
                                      value: 'gasto',
                                      child: Text('Gasto'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'ingreso',
                                      child: Text('Ingreso'),
                                    ),
                                  ],
                                  onChanged: (v) => setState(() => _tipo = v!),
                                ),
                                DropdownButton<String>(
                                  value: _categoria,
                                  items: const [
                                    DropdownMenuItem(
                                      value: 'Transporte',
                                      child: Text('Transporte'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'Comida',
                                      child: Text('Comida'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'Estudios',
                                      child: Text('Estudios'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'Ocio',
                                      child: Text('Ocio'),
                                    ),
                                    DropdownMenuItem(
                                      value: 'Otros',
                                      child: Text('Otros'),
                                    ),
                                  ],
                                  onChanged:
                                      (v) => setState(() => _categoria = v!),
                                ),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(_fechaTexto(_fecha.toIso8601String())),
                                    OutlinedButton(
                                      onPressed: () async {
                                        final picked = await showDatePicker(
                                          context: context,
                                          initialDate: _fecha,
                                          firstDate: DateTime(2020),
                                          lastDate: DateTime(2100),
                                          initialEntryMode:
                                              DatePickerEntryMode.input,
                                        );
                                        if (picked != null) {
                                          setState(() => _fecha = picked);
                                          _cargarLimiteForm();
                                        }
                                      },
                                      child: Text('Cambiar fecha'),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          _indicadorLimiteForm(),
                          TextFormField(
                            enabled: puedeEditarMonto(
                              _editingState ?? 'pendiente',
                            ),

                            controller: _montoController,
                            onChanged: (_) => setState(() {}),
                            decoration: InputDecoration(hintText: 'Monto (Bs)'),
                            validator: (texto) {
                              if (texto == null || texto.isEmpty) {
                                return 'El campo no puede estar vacío';
                              }
                              final n = double.tryParse(texto);
                              if (n == null) {
                                return 'Formato numérico inválido';
                              }
                              if (n <= 0) {
                                return 'El monto debe ser mayor a 0';
                              }
                              return null;
                            },
                          ),

                          if (avisoMonto != null) ...[
                            const SizedBox(height: 4),
                            Text(
                              avisoMonto,
                              style: const TextStyle(
                                color: ColorStyles.errorDefault,
                                fontSize: 12,
                              ),
                            ),
                          ],

                          TextFormField(
                            controller: _descripcionController,
                            decoration: InputDecoration(
                              hintText: 'Descripción (opcional)',
                            ),
                          ),

                          if (!puedeEditarMonto(
                            _editingState ?? 'pendiente',
                          )) ...[
                            const Text(
                              'No es posible modificar el monto porque el movimiento ya fue pagado',
                              style: TextStyle(color: Colors.red, fontSize: 12),
                            ),
                          ],

                          ElevatedButton(
                            onPressed: _guardando ? null : _save,
                            style: ElevatedButton.styleFrom(
                              minimumSize: const Size(double.infinity, 52),
                            ),
                            child:
                                _guardando
                                    ? const SizedBox(
                                      height: 20,
                                      width: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    )
                                    : const Text('Guardar'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
