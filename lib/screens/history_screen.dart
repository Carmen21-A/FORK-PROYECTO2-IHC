import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:presupuesto_estudiantil/design_system/app_text_style.dart';
import 'package:presupuesto_estudiantil/design_system/color_styles.dart';
import 'package:presupuesto_estudiantil/utils/historial.dart';
import 'package:presupuesto_estudiantil/widgets/app_drawer.dart';
import '../services/historial_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final _service = HistorialService();
  List<Map<String, dynamic>> _eventos = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final data = await _service.getHistorial();
    if (mounted) {
      setState(() => _eventos = ordenarRecientePrimero(data));
    }
  }

  String _fechaHora(String iso) {
    final fecha = DateTime.tryParse(iso)?.toLocal();
    if (fecha == null) return '';
    final dia = fecha.day.toString().padLeft(2, '0');
    final mes = fecha.month.toString().padLeft(2, '0');
    final hora = fecha.hour.toString().padLeft(2, '0');
    final minuto = fecha.minute.toString().padLeft(2, '0');
    return '$dia/$mes/${fecha.year} $hora:$minuto';
  }

  String _textoAccion(String accion) {
    switch (accion) {
      case 'creado':
        return 'Movimiento creado';
      case 'editado':
        return 'Movimiento editado';
      case 'eliminado':
        return 'Movimiento eliminado';
      case 'cambio_estado':
        return 'Estado cambiado';
      default:
        return accion;
    }
  }

  IconData _iconoAccion(String accion) {
    switch (accion) {
      case 'creado':
        return Icons.add_circle_outline;
      case 'editado':
        return Icons.edit_outlined;
      case 'eliminado':
        return Icons.delete_outline;
      case 'cambio_estado':
        return Icons.swap_horiz;
      default:
        return Icons.history;
    }
  }

  Color _fondoAccion(String accion) {
    switch (accion) {
      case 'creado':
        return ColorStyles.successLight;
      case 'editado':
        return ColorStyles.primary100;
      case 'eliminado':
        return ColorStyles.errorLight;
      case 'cambio_estado':
        return ColorStyles.warningLight;
      default:
        return ColorStyles.gray100;
    }
  }

  Color _colorAccion(String accion) {
    switch (accion) {
      case 'creado':
        return ColorStyles.successDark;
      case 'editado':
        return ColorStyles.primary300;
      case 'eliminado':
        return ColorStyles.errorDefault;
      case 'cambio_estado':
        return ColorStyles.warningDark;
      default:
        return ColorStyles.grayBase;
    }
  }

  void _verDetalle(Map<String, dynamic> evento) {
    final accion = (evento['accion'] ?? '').toString();
    showModalBottomSheet(
      context: context,
      builder:
          (context) => Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Detalle del evento', style: AppTextStyle.boldBodyLarge),
                const SizedBox(height: 12),
                _filaDetalle('Acción', _textoAccion(accion)),
                _filaDetalle('Detalle', (evento['detalle'] ?? '').toString()),
                _filaDetalle(
                  'Fecha',
                  _fechaHora((evento['created_at'] ?? '').toString()),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cerrar'),
                  ),
                ),
              ],
            ),
          ),
    );
  }

  Widget _filaDetalle(String etiqueta, String valor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              etiqueta,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(valor)),
        ],
      ),
    );
  }

  Widget _estadoVacio() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 64, color: ColorStyles.gray300),
            const SizedBox(height: 12),
            Text(
              'Aún no hay movimientos registrados',
              style: AppTextStyle.boldBodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              'Registra tu primer movimiento y aparecerá aquí.',
              style: AppTextStyle.regularBodySmall.copyWith(
                color: ColorStyles.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go('/movements'),
              child: const Text('Registrar movimiento'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _filaEvento(Map<String, dynamic> evento) {
    final accion = (evento['accion'] ?? '').toString();
    final detalle = (evento['detalle'] ?? '').toString();
    final fecha = _fechaHora((evento['created_at'] ?? '').toString());

    return ListTile(
      leading: CircleAvatar(
        backgroundColor: _fondoAccion(accion),
        child: Icon(
          _iconoAccion(accion),
          color: _colorAccion(accion),
          size: 20,
        ),
      ),
      title: Text(
        _textoAccion(accion),
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      subtitle: Text('$detalle\n$fecha'),
      isThreeLine: true,
      onTap: () => _verDetalle(evento),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: const AppDrawer(),
      appBar: AppBar(
        title: const Text('Historial'),
        actions: [
          IconButton(
            tooltip: 'Actualizar',
            onPressed: _load,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body:
          _eventos.isEmpty
              ? _estadoVacio()
              : ListView.separated(
                itemCount: _eventos.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) => _filaEvento(_eventos[index]),
              ),
    );
  }
}
