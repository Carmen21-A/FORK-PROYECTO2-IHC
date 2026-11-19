// Tokens de diseño: los valores viven SOLO en src/design_system/tokens.css (:root).
// El resto del código los llama con var(--nombre). Si alguien escribe un color a mano, esta prueba falla.
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

const SRC = join(__dirname, '../../src')
const TOKENS = join(SRC, 'design_system/tokens.css')

function archivos(dir) {
  return readdirSync(dir).flatMap((n) => {
    const ruta = join(dir, n)
    if (statSync(ruta).isDirectory()) return archivos(ruta)
    return /\.(vue|css|js)$/.test(n) ? [ruta] : []
  })
}

// Quita los comentarios para no confundir un texto explicativo con código
const sinComentarios = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '').replace(/<!--[\s\S]*?-->/g, '')
const COLOR = /#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/
const definidos = new Set([...readFileSync(TOKENS, 'utf8').matchAll(/^\s*(--[a-z0-9-]+):/gm)].map((m) => m[1]))

describe('tokens de diseño', () => {
  it('ningún archivo fuera de tokens.css escribe colores a mano', () => {
    const conColores = []
    for (const f of archivos(SRC).filter((f) => f !== TOKENS)) {
      sinComentarios(readFileSync(f, 'utf8')).split('\n').forEach((linea, i) => {
        if (COLOR.test(linea)) conColores.push(`${relative(SRC, f)}:${i + 1}  ${linea.trim()}`)
      })
    }
    expect(conColores).toEqual([])
  })

  it('no se usa var(--x, #respaldo): cada token existe en tokens.css', () => {
    const problemas = []
    for (const f of archivos(SRC).filter((f) => f !== TOKENS)) {
      for (const m of sinComentarios(readFileSync(f, 'utf8')).matchAll(/var\((--[a-z0-9-]+)\s*(,)?/g)) {
        if (m[2]) problemas.push(`${relative(SRC, f)}: ${m[1]} con valor de respaldo`)
        else if (!definidos.has(m[1])) problemas.push(`${relative(SRC, f)}: ${m[1]} no existe en tokens.css`)
      }
    }
    expect(problemas).toEqual([])
  })

  it('los tokens tienen nombres por función, en español', () => {
    for (const nombre of definidos) {
      expect(nombre).toMatch(/^--(color|degradado|sombra|espacio|radio|fuente|texto)(-[a-z0-9]+)*$/)
    }
  })
})
