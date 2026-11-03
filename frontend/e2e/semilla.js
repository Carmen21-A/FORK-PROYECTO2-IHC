// Ejecuta backend/semilla.py con el Python del entorno virtual del backend.
// Lo usan "pnpm semilla", la configuracion de Playwright y las pruebas que cambian datos.
import { execFileSync } from 'node:child_process' // importa execFileSync para ejecutar procesos sincrónicos en node
import { existsSync } from 'node:fs' // importa existsSync para comprobar si un archivo existe en el disco
import { fileURLToPath } from 'node:url' // importa fileURLToPath para convertir urls de módulos a rutas de archivo
import path from 'node:path' // importa el módulo path para manejar rutas de directorios y archivos

export const BASE_E2E = 'budget_e2e' // define y exporta la constante con el nombre de la base de datos de pruebas e2e
export const carpetaBackend = fileURLToPath(new URL('../../backend', import.meta.url)) // calcula y exporta la ruta absoluta de la carpeta backend

// Windows guarda el Python del venv en Scripts/, Mac y Linux en bin/
export const python = [ // exporta la ruta del ejecutable de python buscando en el entorno virtual
  path.join(carpetaBackend, '.venv', 'Scripts', 'python.exe'), // ruta típica de python en windows dentro de .venv
  path.join(carpetaBackend, '.venv', 'bin', 'python'), // ruta típica de python en linux o mac dentro de .venv
].find(existsSync) ?? 'python' // toma la primera ruta que exista en disco o usa 'python' del sistema por defecto

export function sembrar() { // define y exporta la función sembrar para poblar la base de datos de prueba
  try { // bloque try para capturar cualquier error al ejecutar el script de python
    execFileSync(python, ['semilla.py'], { // ejecuta el comando python semilla.py de forma síncrona
      cwd: carpetaBackend, // define el directorio de trabajo donde se ejecutará el script (backend)
      env: { ...process.env, DATABASE_NAME: BASE_E2E }, // pasa las variables de entorno indicando la base de datos e2e
      stdio: ['ignore', 'inherit', 'pipe'], // ignora stdin, muestra stdout directamente y captura stderr en un pipe
    }) // fin de las opciones de ejecución
  } catch (error) { // captura el error si la ejecución de semilla.py falla
    // Muestra el error de Python (no solo "Command failed")
    throw new Error(`La semilla falló:\n${error.stderr?.toString() ?? error.message}`) // lanza una excepción con el mensaje de error capturado
  } // fin del bloque catch
} // fin de la función sembrar

// Playwright lo usa como globalSetup: se siembra una vez antes de todas las pruebas
export default sembrar // exporta la función sembrar por defecto para que playwright la use como setup global

// "pnpm semilla" ejecuta este archivo directamente
if (process.argv[1] === fileURLToPath(import.meta.url)) sembrar() // si el archivo se ejecuta directamente desde la consola, llama a sembrar
