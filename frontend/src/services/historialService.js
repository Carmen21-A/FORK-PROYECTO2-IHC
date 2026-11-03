// Portado de lib/services/historial_service.dart
// (los eventos los registra el backend al crear, editar, cambiar estado o eliminar)
import { api } from './api.js'

export const HistorialService = {
  // Trae los eventos del usuario, reciente primero
  async getHistorial() {
    return api('/historial')
  },
}
