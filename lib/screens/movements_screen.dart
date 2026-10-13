import 'package:flutter/material.dart';
import 'package:presupuesto_estudiantil/utils/estado_movimiento.dart';
import 'package:presupuesto_estudiantil/widgets/app_drawer.dart';
import '../services/movements_service.dart';
import 'package:presupuesto_estudiantil/utils/limite_mensual.dart';
import 'package:presupuesto_estudiantil/services/limites_service.dart';

class MovementsScreen extends StatefulWidget {
  const MovementsScreen({super.key});

  @override
  State<MovementsScreen> createState() => _MovementsScreenState();
}

class _MovementsScreenState extends State<MovementsScreen> {
  final _formularioId = GlobalKey<FormState>();
  final _montoController = TextEditingController();
  final _service = MovementsService();
  final _limitesService = LimitesService();

  String _tipo = 'gasto';
  String _categoria = 'Transporte';
  DateTime _fecha = DateTime.now();
  List<Map<String, dynamic>> _movimientos = [];
  String? _editingId;
  String? _editingState;
  double? _limiteMensual;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _montoController.dispose();
    super.dispose();
  }

  // Esto cargara los movimientos y el limite mensual
  Future<void> _load() async {
    final data = await _service.getAll();
    final mesActual =
        '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}';
    final limite = await _limitesService.getLimit(mesActual);
    if (mounted) {
      setState(() {
        _movimientos = data;
        _limiteMensual = limite;
      });
    }
  }

  Widget _tarjetaResumenLimite() {
    final mesActual =
        '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}';
    final gastoActual = calcularGastoTotalMes(_movimientos, mesActual);
    final limite = _limiteMensual;
    final disponible = limite != null ? (limite - gastoActual) : null;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Gastado: $gastoActual Bs / Limite: ${limite != null ? "$limite Bs" : "Sin definir"}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    limite != null
                        ? 'Disponible: ${disponible! >= 0 ? disponible : 0} Bs'
                        : 'Define un limite para controlar tus gastos',
                    style: TextStyle(
                      color:
                          (disponible != null && disponible <= 0)
                              ? Colors.red
                              : Colors.grey.shade800,
                    ),
                  ),
                ],
              ),
            ),
            TextButton.icon(
              onPressed: _dialogoCambiarLimite,
              icon: const Icon(Icons.edit, size: 16),
              label: Text(limite == null ? 'Definir' : 'Cambiar'),
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
    final formKey = GlobalKey<FormState>();
    final mesActual =
        '${DateTime.now().year}-${DateTime.now().month.toString().padLeft(2, '0')}';
    final gastoActual = calcularGastoTotalMes(_movimientos, mesActual);

    await showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: const Text('Limite mensual de gastos'),
            content: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Gasto actual del mes: $gastoActual Bs'),
                  const SizedBox(height: 10),
                  TextFormField(
                    controller: controller,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Nuevo limite (Bs)',
                      hintText: 'Ej: 500',
                    ),
                    validator: (valor) {
                      // Que no este vacio, sin letras y solo numeros
                      final errorFormato = validarMontoLimite(valor);
                      if (errorFormato != null) return errorFormato;

                      // Verifica que no sea menor a lo ya gastado
                      final n = double.parse(valor!);
                      if (esLimiteMenorAGasto(n, gastoActual)) {
                        return 'No puede ser menor a lo ya gastado ($gastoActual Bs)';
                      }
                      return null;
                    },
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancelar'),
              ),
              ElevatedButton(
                onPressed: () async {
                  if (!formKey.currentState!.validate()) return;
                  final nuevoLimite = double.parse(controller.text);
                  await _limitesService.saveMonthLimit(
                    mes: mesActual,
                    limite: nuevoLimite,
                  );
                  if (mounted) {
                    Navigator.pop(ctx);
                    _load();
                  }
                },
                child: const Text('Guardar'),
              ),
            ],
          ),
    );
  }

  Future<bool> _validateOverLimit(double monto) async {
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
            backgroundColor: Colors.red,
            content: Text(
              'No se puede registrar, porque supera tu limite mensual de $limite bs (llevas gastando $gastoActual bs)',
            ),
          ),
        );
      }
      return true; // Se excedio
    }

    return false; // No se excedio
  }

  Future<void> _save() async {
    if (!_formularioId.currentState!.validate()) return;
    final monto = double.tryParse(_montoController.text) ?? 0;

    final excede = await _validateOverLimit(monto);
    if (excede) return;

    try {
      if (_editingId == null) {
        //Se esta creando un uno
        await _service.create(
          tipo: _tipo,
          monto: monto,
          categoria: _categoria,
          fecha: _fecha,
        );
      } else {
        // Se esta editando uno movimiento existente
        await _service.update(
          id: _editingId!,
          tipo: _tipo,
          monto: monto,
          categoria: _categoria,
          fecha: _fecha,
        );
        _editingId = null;
        _editingState = null;
      }

      if (mounted) {
        // Se vuevle a cargar la lista
        _load();
      }
    } catch (_) {}

    _montoController.text = "";
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
      _tipo = m['tipo'] as String;
      _categoria = m['categoria'] as String;
      _fecha = DateTime.parse(m['fecha'] as String);
      _editingState = m['estado'] as String;
    });
  }

  Future<void> _confirmDeletion(String id) async {
    final responder = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Confirma que quieres eliminar este movimiento'),
            content: const Text(
              '¿Estas seguro que quieres eliminar este movimiento?',
            ),
            actions: [
              TextButton(
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

  Future<void> _cambiarEstado(Map<String, dynamic> m) async {
    final actual = m['estado'];
    final siguiente = siguienteEstado(actual);
    if (siguiente == null) return;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: const AppDrawer(),
      appBar: AppBar(title: const Text('Movimientos')),
      body: Column(
        children: [
          _tarjetaResumenLimite(),
          Expanded(
            child: ListView(
              children: [
                ..._movimientos.map((m) {
                  final tipo = m['tipo'] as String;
                  final monto = m['monto'];
                  final categoria = m['categoria'];
                  final fecha = _fechaTexto(m['fecha'] as String);
                  final etiqueta = tipo == 'gasto' ? 'Gasto' : 'Ingreso';

                  return ListTile(
                    title: Text('$etiqueta - $monto Bs - $categoria - $fecha'),
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
                        ElevatedButton(
                          onPressed: () => _confirmDeletion(m['id'] as String),
                          child: const Text('Borrar'),
                        ),

                        TextButton(
                          onPressed: () => _prepareEdition(m),
                          child: const Text('Editar'),
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

                                  TextButton(
                                    onPressed: () {
                                      setState(() {
                                        _editingId = null;
                                        _editingState = null;
                                        _montoController.clear();
                                      });
                                    },
                                    child: const Text('Cancelar'),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
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
                                    TextButton(
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
                                        }
                                      },
                                      child: Text('Cambiar fecha'),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          TextFormField(
                            enabled: puedeEditarMonto(
                              _editingState ?? 'pendiente',
                            ),

                            controller: _montoController,
                            decoration: InputDecoration(hintText: 'Monto (Bs)'),
                            validator: (texto) {
                              if (texto == null || texto.isEmpty) {
                                return 'El campo no puede estar vacio';
                              }
                              final n = double.tryParse(texto);
                              if (n == null) {
                                return 'Formato numerico invalido';
                              }
                              if (n <= 0) {
                                return 'El monto debe ser mayor a 0';
                              }
                              return null;
                            },
                          ),

                          if (!puedeEditarMonto(
                            _editingState ?? 'pendiente',
                          )) ...[
                            const SizedBox(height: 4),
                            const Text(
                              'No es posible modificar el monto porque el movimiento ya fue pagado',
                              style: TextStyle(color: Colors.red, fontSize: 12),
                            ),
                          ],

                          ElevatedButton(
                            onPressed: _save,
                            style: ElevatedButton.styleFrom(
                              minimumSize: const Size(double.infinity, 52),
                            ),
                            child: const Text('Guardar'),
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
