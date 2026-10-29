import 'package:flutter/material.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:presupuesto_estudiantil/design_system/color_styles.dart';
import 'package:presupuesto_estudiantil/design_system/spacing_tokens.dart';
import 'package:presupuesto_estudiantil/services/movements_service.dart';
import 'package:presupuesto_estudiantil/services/presupuestos_service.dart';
import 'package:presupuesto_estudiantil/utils/presupuesto_categoria.dart';
import 'package:presupuesto_estudiantil/widgets/app_drawer.dart';

class PresupuestoCategoriaScreen extends StatefulWidget {
  //clase PresupuestoCategoriaScreen  esta clase hereda todas las propiedades y comportamientos de la clase base de Flutter para widgets con estado.
  const PresupuestoCategoriaScreen({
    super.key,
  }); //acepta una clave de identificación opcional (super.key).

  @override //estás sobrescribiendo (reemplazando) un método que ya existía en la clase padre (StatefulWidget)
  State<PresupuestoCategoriaScreen>
  createState() => //Crea y devuelve el estado de la pantalla PresupuestoCategoriaScreen
      _PresupuestoCategoriaScreenState(); // usando la clase _PresupuestoCategoriaScreenState
}

class _PresupuestoCategoriaScreenState
    extends State<PresupuestoCategoriaScreen> {
  //Hereda de la clase de Estado correspondiente a la pantalla PresupuestoCategoriaScreen
  final _presupuestosService = PresupuestosService();
  final _movementsService = MovementsService();

  late DateTime _mesSeleccionado;
  bool _cargando = true;
  String? _error;

  List<Map<String, dynamic>> _movimientos = [];
  ResumenPresupuestoMensual? _resumen;
  String? _categoriaDetalleExpandida;

  String get _mesClave =>
      '${_mesSeleccionado.year}-${_mesSeleccionado.month.toString().padLeft(2, '0')}';

  final Map<String, IconData> _iconosCategoria = {
    'Transporte': Icons.directions_bus_rounded,
    'Comida': Icons.restaurant_rounded,
    'Estudios': Icons.school_rounded,
    'Ocio': Icons.sports_esports_rounded,
    'Otros': Icons.category_rounded,
  };

  final Map<String, Color> _coloresCategoria = {
    'Transporte': const Color(0xFF0284C7),
    'Comida': const Color(0xFFEA580C),
    'Estudios': const Color(0xFF7C3AED),
    'Ocio': const Color(0xFFDB2777),
    'Otros': const Color(0xFF475569),
  };

  @override
  void initState() {
    super.initState();
    final hoy = DateTime.now();
    _mesSeleccionado = DateTime(hoy.year, hoy.month);
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    setState(() {
      _cargando = true;
      _error = null;
    });

    try {
      final movimientos = await _movementsService.getAll();
      final resumen = await _presupuestosService.getResumenMensual(
        mes: _mesClave,
        movimientos: movimientos,
      );

      if (mounted) {
        setState(() {
          _movimientos = movimientos;
          _resumen = resumen;
          _cargando = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Error al cargar presupuestos: $e';
          _cargando = false;
        });
      }
    }
  }

  void _cambiarMes(int offset) {
    setState(() {
      _mesSeleccionado = DateTime(
        _mesSeleccionado.year,
        _mesSeleccionado.month + offset,
      );
      _categoriaDetalleExpandida = null;
    });
    _cargarDatos();
  }

  String _nombreMes(int mes) {
    const nombres = [
      'Enero',
      'Febrero',
      'Marzo',
      'Abril',
      'Mayo',
      'Junio',
      'Julio',
      'Agosto',
      'Septiembre',
      'Octubre',
      'Noviembre',
      'Diciembre',
    ];
    return nombres[mes - 1];
  }

  Future<void> _abrirDialogoPresupuesto({
    required String categoria,
    required double valorActual,
  }) async {
    final formKey = GlobalKey<FormState>();
    final controller = TextEditingController(
      text: valorActual > 0 ? valorActual.toStringAsFixed(2) : '',
    );
    bool guardando = false;

    await showDialog(
      context: context,
      builder:
          (ctx) => StatefulBuilder(
            builder: (context, setModalState) {
              return AlertDialog(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                title: Row(
                  children: [
                    Icon(
                      _iconosCategoria[categoria] ?? Icons.pie_chart,
                      color:
                          _coloresCategoria[categoria] ??
                          ColorStyles.primaryBase,
                    ),
                    const SizedBox(width: SpacingTokens.s),
                    Expanded(
                      child: Text(
                        'Presupuesto: $categoria',
                        style: AppTextStyle.boldBodyLarge,
                      ),
                    ),
                  ],
                ),
                content: Form(
                  key: formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Define el monto límite mensual para ${_nombreMes(_mesSeleccionado.month)} ${_mesSeleccionado.year}',
                        style: AppTextStyle.regularCaption.copyWith(
                          color: ColorStyles.textSecondary,
                        ),
                      ),
                      const SizedBox(height: SpacingTokens.m),
                      TextFormField(
                        controller: controller,
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        autofocus: true,
                        decoration: InputDecoration(
                          labelText: 'Monto mensual (Bs.)',
                          prefixText: 'Bs. ',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          hintText: 'Ej. 300.00',
                        ),
                        validator: validarMontoPresupuesto,
                      ),
                      const SizedBox(height: SpacingTokens.s),
                      Wrap(
                        spacing: 8,
                        children:
                            [50, 100, 200, 500].map((monto) {
                              return ActionChip(
                                label: Text('+$monto Bs'),
                                onPressed: () {
                                  final actual =
                                      double.tryParse(controller.text) ?? 0.0;
                                  controller.text = (actual + monto)
                                      .toStringAsFixed(2);
                                },
                              );
                            }).toList(),
                      ),
                    ],
                  ),
                ),
                actions: [
                  TextButton(
                    onPressed: guardando ? null : () => Navigator.pop(ctx),
                    child: const Text('Cancelar'),
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: ColorStyles.primaryBase,
                      foregroundColor: ColorStyles.textInverse,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    onPressed:
                        guardando
                            ? null
                            : () async {
                              if (!formKey.currentState!.validate()) return;

                              final nuevoMonto = double.parse(
                                controller.text.trim(),
                              );
                              setModalState(() => guardando = true);

                              try {
                                await _presupuestosService
                                    .savePresupuestoCategoria(
                                      mes: _mesClave,
                                      categoria: categoria,
                                      monto: nuevoMonto,
                                    );

                                if (ctx.mounted) {
                                  Navigator.pop(ctx);
                                  _cargarDatos();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      backgroundColor:
                                          ColorStyles.successDefault,
                                      content: Text(
                                        'Presupuesto para $categoria actualizado a Bs. ${nuevoMonto.toStringAsFixed(2)}',
                                      ),
                                    ),
                                  );
                                }
                              } catch (e) {
                                setModalState(() => guardando = false);
                                if (ctx.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      backgroundColor: ColorStyles.errorDefault,
                                      content: Text('Error al guardar: $e'),
                                    ),
                                  );
                                }
                              }
                            },
                    child:
                        guardando
                            ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                            : const Text('Guardar'),
                  ),
                ],
              );
            },
          ),
    );
  }

  Future<void> _eliminarPresupuesto(String categoria) async {
    final confirmar = await showDialog<bool>(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: Text('Eliminar presupuesto de $categoria'),
            content: const Text(
              '¿Estás seguro de quitar el presupuesto de esta categoría para este mes?',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx, false),
                child: const Text('Cancelar'),
              ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: ColorStyles.errorDefault,
                  foregroundColor: ColorStyles.textInverse,
                ),
                onPressed: () => Navigator.pop(ctx, true),
                child: const Text('Eliminar'),
              ),
            ],
          ),
    );

    if (confirmar == true) {
      await _presupuestosService.deletePresupuestoCategoria(
        mes: _mesClave,
        categoria: categoria,
      );
      _cargarDatos();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: ColorStyles.gray600,
            content: Text('Presupuesto de $categoria eliminado'),
          ),
        );
      }
    }
  }

  List<Map<String, dynamic>> _movimientosDeCategoria(String categoria) {
    return _movimientos.where((m) {
      final fechaStr = (m['fecha'] ?? '').toString();
      final tipo = (m['tipo'] ?? '').toString();
      final estado = (m['estado'] ?? '').toString();
      final cat = (m['categoria'] ?? '').toString();

      return fechaStr.startsWith(_mesClave) &&
          tipo == 'gasto' &&
          estado != 'cancelado' &&
          cat == categoria;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Presupuesto por Categoría'),
        backgroundColor: ColorStyles.primaryBase,
        foregroundColor: ColorStyles.textInverse,
        elevation: 1,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualizar',
            onPressed: _cargarDatos,
          ),
        ],
      ),
      drawer: const AppDrawer(),
      body:
          _cargando
              ? const Center(child: CircularProgressIndicator())
              : _error != null
              ? Center(
                child: Padding(
                  padding: const EdgeInsets.all(SpacingTokens.l),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 48,
                        color: ColorStyles.errorDefault,
                      ),
                      const SizedBox(height: SpacingTokens.m),
                      Text(
                        _error!,
                        style: AppTextStyle.mediumBodyMedium,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: SpacingTokens.m),
                      ElevatedButton(
                        onPressed: _cargarDatos,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                ),
              )
              : RefreshIndicator(
                onRefresh: _cargarDatos,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(SpacingTokens.m),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 850),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _construirNavegacionMes(),
                          const SizedBox(height: SpacingTokens.m),
                          if (_resumen != null) ...[
                            _construirTarjetaResumen(_resumen!),
                            const SizedBox(height: SpacingTokens.m),
                            if (_resumen!.categoriasExcedidas.isNotEmpty ||
                                _resumen!.categoriasAlerta.isNotEmpty)
                              _construirBannerAlertas(_resumen!),
                            const SizedBox(height: SpacingTokens.m),
                            _construirListaCategorias(_resumen!),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
              ),
    );
  }

  Widget _construirNavegacionMes() {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: SpacingTokens.m,
          vertical: SpacingTokens.s,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            IconButton(
              icon: const Icon(Icons.chevron_left),
              tooltip: 'Mes anterior',
              onPressed: () => _cambiarMes(-1),
            ),
            Row(
              children: [
                const Icon(
                  Icons.calendar_month,
                  color: ColorStyles.primaryBase,
                  size: 20,
                ),
                const SizedBox(width: SpacingTokens.s),
                Text(
                  '${_nombreMes(_mesSeleccionado.month)} ${_mesSeleccionado.year}',
                  style: AppTextStyle.boldBodyLarge.copyWith(
                    color: ColorStyles.textPrimary,
                  ),
                ),
              ],
            ),
            IconButton(
              icon: const Icon(Icons.chevron_right),
              tooltip: 'Mes siguiente',
              onPressed: () => _cambiarMes(1),
            ),
          ],
        ),
      ),
    );
  }

  Widget _construirTarjetaResumen(ResumenPresupuestoMensual resumen) {
    final porcentajeVisual = (resumen.porcentajeTotal * 100).clamp(0.0, 999.0);
    final estaExcedidoTotal = resumen.totalRestante < 0;

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [ColorStyles.primaryBase, ColorStyles.primary300],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: ColorStyles.primaryBase.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(SpacingTokens.l),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Resumen Mensual por Categoría',
                style: AppTextStyle.boldBodyMedium.copyWith(
                  color: ColorStyles.textInverse,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${porcentajeVisual.toStringAsFixed(1)}% consumido',
                  style: AppTextStyle.boldMicro.copyWith(
                    color: ColorStyles.textInverse,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: SpacingTokens.m),
          Row(
            children: [
              Expanded(
                child: _columnaMetrica(
                  titulo: 'Presupuestado',
                  valor: 'Bs. ${resumen.totalPresupuestado.toStringAsFixed(2)}',
                  icono: Icons.account_balance_wallet_outlined,
                ),
              ),
              Container(
                height: 40,
                width: 1,
                color: Colors.white.withOpacity(0.3),
              ),
              Expanded(
                child: _columnaMetrica(
                  titulo: 'Consumido',
                  valor: 'Bs. ${resumen.totalConsumido.toStringAsFixed(2)}',
                  icono: Icons.shopping_cart_outlined,
                ),
              ),
              Container(
                height: 40,
                width: 1,
                color: Colors.white.withOpacity(0.3),
              ),
              Expanded(
                child: _columnaMetrica(
                  titulo: estaExcedidoTotal ? 'Exceso' : 'Restante',
                  valor:
                      'Bs. ${resumen.totalRestante.abs().toStringAsFixed(2)}',
                  icono:
                      estaExcedidoTotal
                          ? Icons.warning_amber_rounded
                          : Icons.savings_outlined,
                ),
              ),
            ],
          ),
          const SizedBox(height: SpacingTokens.m),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value:
                  resumen.totalPresupuestado > 0
                      ? resumen.porcentajeTotal.clamp(0.0, 1.0)
                      : 0.0,
              minHeight: 8,
              backgroundColor: Colors.white.withOpacity(0.25),
              valueColor: AlwaysStoppedAnimation<Color>(
                estaExcedidoTotal
                    ? ColorStyles.errorDefault
                    : resumen.porcentajeTotal >= 0.8
                    ? ColorStyles.warningDefault
                    : Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _columnaMetrica({
    required String titulo,
    required String valor,
    required IconData icono,
  }) {
    return Column(
      children: [
        Icon(icono, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(
          titulo,
          style: AppTextStyle.regularMicro.copyWith(color: Colors.white70),
        ),
        const SizedBox(height: 2),
        Text(
          valor,
          style: AppTextStyle.boldBodySmall.copyWith(
            color: ColorStyles.textInverse,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _construirBannerAlertas(ResumenPresupuestoMensual resumen) {
    final excedidas = resumen.categoriasExcedidas;
    final alertas = resumen.categoriasAlerta;

    return Container(
      decoration: BoxDecoration(
        color:
            excedidas.isNotEmpty
                ? ColorStyles.errorLight
                : ColorStyles.warningLight,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color:
              excedidas.isNotEmpty
                  ? ColorStyles.errorDefault.withOpacity(0.4)
                  : ColorStyles.warningDefault.withOpacity(0.4),
        ),
      ),
      padding: const EdgeInsets.all(SpacingTokens.m),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            excedidas.isNotEmpty ? Icons.error_outline : Icons.warning_amber,
            color:
                excedidas.isNotEmpty
                    ? ColorStyles.errorDark
                    : ColorStyles.warningDark,
          ),
          const SizedBox(width: SpacingTokens.m),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (excedidas.isNotEmpty)
                  Text(
                    '¡Límite superado en: ${excedidas.join(", ")}!',
                    style: AppTextStyle.boldCaption.copyWith(
                      color: ColorStyles.errorDark,
                    ),
                  ),
                if (alertas.isNotEmpty)
                  Text(
                    'Cerca del límite (>= 80%): ${alertas.join(", ")}',
                    style: AppTextStyle.regularCaption.copyWith(
                      color: ColorStyles.warningDark,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _construirListaCategorias(ResumenPresupuestoMensual resumen) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Categorías de Gastos',
          style: AppTextStyle.boldHeadingSmall.copyWith(
            color: ColorStyles.textPrimary,
          ),
        ),
        const SizedBox(height: SpacingTokens.s),
        Text(
          'Monitorea el consumo real frente al límite fijado para cada categoría',
          style: AppTextStyle.regularCaption.copyWith(
            color: ColorStyles.textSecondary,
          ),
        ),
        const SizedBox(height: SpacingTokens.m),
        ...resumen.items.map((item) => _construirTarjetaCategoria(item)),
      ],
    );
  }

  Widget _construirTarjetaCategoria(ItemPresupuestoCategoria item) {
    final color = _coloresCategoria[item.categoria] ?? ColorStyles.primaryBase;
    final icono = _iconosCategoria[item.categoria] ?? Icons.pie_chart;
    final estaExpandido = _categoriaDetalleExpandida == item.categoria;

    Color colorEstado;
    String textoEstado;
    IconData iconoEstado;

    switch (item.estado) {
      case EstadoPresupuesto.excedido:
        colorEstado = ColorStyles.errorDefault;
        textoEstado =
            'Excedido por Bs. ${item.restante.abs().toStringAsFixed(2)}';
        iconoEstado = Icons.cancel;
        break;
      case EstadoPresupuesto.alerta:
        colorEstado = ColorStyles.warningDefault;
        textoEstado =
            'Alerta: ${(item.porcentaje * 100).toStringAsFixed(0)}% consumido';
        iconoEstado = Icons.warning_amber_rounded;
        break;
      case EstadoPresupuesto.optimo:
        colorEstado = ColorStyles.successDefault;
        textoEstado =
            'En orden: ${(item.porcentaje * 100).toStringAsFixed(0)}% consumido';
        iconoEstado = Icons.check_circle;
        break;
      case EstadoPresupuesto.sinPresupuesto:
        colorEstado = ColorStyles.gray300;
        textoEstado = 'Sin presupuesto fijado';
        iconoEstado = Icons.info_outline;
        break;
    }

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: SpacingTokens.m),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(
          color:
              item.estaExcedido
                  ? ColorStyles.errorDefault.withOpacity(0.5)
                  : Colors.transparent,
          width: 1.5,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SpacingTokens.m),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: color.withOpacity(0.12),
                  child: Icon(icono, color: color, size: 22),
                ),
                const SizedBox(width: SpacingTokens.m),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.categoria,
                        style: AppTextStyle.boldBodyMedium.copyWith(
                          color: ColorStyles.textPrimary,
                        ),
                      ),
                      Row(
                        children: [
                          Icon(iconoEstado, size: 14, color: colorEstado),
                          const SizedBox(width: 4),
                          Text(
                            textoEstado,
                            style: AppTextStyle.boldMicro.copyWith(
                              color: colorEstado,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                IconButton(
                  tooltip:
                      item.tienePresupuesto
                          ? 'Editar presupuesto'
                          : 'Definir presupuesto',
                  icon: Icon(
                    item.tienePresupuesto
                        ? Icons.edit_outlined
                        : Icons.add_circle,
                    color: ColorStyles.primaryBase,
                  ),
                  onPressed:
                      () => _abrirDialogoPresupuesto(
                        categoria: item.categoria,
                        valorActual: item.presupuestado,
                      ),
                ),
                if (item.tienePresupuesto)
                  IconButton(
                    tooltip: 'Eliminar presupuesto',
                    icon: const Icon(
                      Icons.delete_outline,
                      color: ColorStyles.errorDefault,
                      size: 20,
                    ),
                    onPressed: () => _eliminarPresupuesto(item.categoria),
                  ),
              ],
            ),
            const SizedBox(height: SpacingTokens.m),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value:
                    item.tienePresupuesto
                        ? item.porcentaje.clamp(0.0, 1.0)
                        : 0.0,
                minHeight: 8,
                backgroundColor: ColorStyles.gray100,
                valueColor: AlwaysStoppedAnimation<Color>(colorEstado),
              ),
            ),
            const SizedBox(height: SpacingTokens.s),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Presupuesto',
                      style: AppTextStyle.regularMicro.copyWith(
                        color: ColorStyles.textSecondary,
                      ),
                    ),
                    Text(
                      item.tienePresupuesto
                          ? 'Bs. ${item.presupuestado.toStringAsFixed(2)}'
                          : 'No definido',
                      style: AppTextStyle.boldCaption,
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      'Consumido (${item.cantidadMovimientos} gastos)',
                      style: AppTextStyle.regularMicro.copyWith(
                        color: ColorStyles.textSecondary,
                      ),
                    ),
                    Text(
                      'Bs. ${item.consumido.toStringAsFixed(2)}',
                      style: AppTextStyle.boldCaption.copyWith(
                        color: colorEstado,
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      item.estaExcedido ? 'Exceso' : 'Disponible',
                      style: AppTextStyle.regularMicro.copyWith(
                        color: ColorStyles.textSecondary,
                      ),
                    ),
                    Text(
                      item.tienePresupuesto
                          ? 'Bs. ${item.restante.abs().toStringAsFixed(2)}'
                          : '—',
                      style: AppTextStyle.boldCaption.copyWith(
                        color:
                            item.estaExcedido
                                ? ColorStyles.errorDefault
                                : ColorStyles.successDefault,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            if (item.cantidadMovimientos > 0) ...[
              const Divider(height: 24),
              InkWell(
                onTap: () {
                  setState(() {
                    _categoriaDetalleExpandida =
                        estaExpandido ? null : item.categoria;
                  });
                },
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      estaExpandido
                          ? 'Ocultar gastos'
                          : 'Ver los ${item.cantidadMovimientos} gastos de ${item.categoria}',
                      style: AppTextStyle.mediumMicro.copyWith(
                        color: ColorStyles.primaryBase,
                      ),
                    ),
                    Icon(
                      estaExpandido
                          ? Icons.keyboard_arrow_up
                          : Icons.keyboard_arrow_down,
                      size: 16,
                      color: ColorStyles.primaryBase,
                    ),
                  ],
                ),
              ),
              if (estaExpandido) ...[
                const SizedBox(height: SpacingTokens.s),
                _construirDetalleMovimientos(item.categoria),
              ],
            ],
          ],
        ),
      ),
    );
  }

  Widget _construirDetalleMovimientos(String categoria) {
    final movimientos = _movimientosDeCategoria(categoria);
    if (movimientos.isEmpty) {
      return const Text('No hay movimientos registrados');
    }

    return Container(
      decoration: BoxDecoration(
        color: ColorStyles.gray100.withOpacity(0.3),
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.all(SpacingTokens.s),
      child: Column(
        children:
            movimientos.map((m) {
              final descripcion =
                  (m['descripcion'] ?? 'Sin descripción').toString();
              final monto = (m['monto'] as num).toDouble();
              final fecha = (m['fecha'] ?? '').toString();
              final estado = (m['estado'] ?? 'pendiente').toString();

              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(descripcion, style: AppTextStyle.mediumCaption),
                          Text(
                            '$fecha • Estado: $estado',
                            style: AppTextStyle.regularMicro.copyWith(
                              color: ColorStyles.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Text(
                      '-Bs. ${monto.toStringAsFixed(2)}',
                      style: AppTextStyle.boldCaption.copyWith(
                        color: ColorStyles.errorDefault,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
      ),
    );
  }
}
