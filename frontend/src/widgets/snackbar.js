// Equivale a ScaffoldMessenger.of(context).showSnackBar(...)
import { reactive } from 'vue'

export const snackbars = reactive([])
let siguienteId = 0

export function showSnackBar(texto, color = null, duracionMs = 4000) {
  const id = siguienteId++
  snackbars.push({ id, texto, color })
  setTimeout(() => {
    const indice = snackbars.findIndex((s) => s.id === id)
    if (indice !== -1) snackbars.splice(indice, 1)
  }, duracionMs)
}
