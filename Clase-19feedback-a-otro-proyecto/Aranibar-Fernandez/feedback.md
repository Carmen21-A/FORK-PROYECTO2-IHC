# Feedback a otro proyecto - Clase 19

- **Nombre completo del evaluador:** Carmen Jenifer Aranibar Fernandez
- **Mi grupo y caso de estudio:** Presupuesto Estudiantil (Grupo Carmen Aranibar)
- **Grupo y caso de estudio evaluado:** Moises David Cisneros Laura & Erick Raúl Terán Tabera — **Planazo**
- **Integrantes del proyecto evaluado:** Moises David Cisneros Laura, Erick Raúl Terán Tabera
- **URL de la app y repositorio evaluado:** [https://github.com/moises-cisneros/Proyecto2IHC](https://github.com/moises-cisneros/Proyecto2IHC)
- **Fecha y versión/commit probado (si está disponible):** 03/11/2026 (Versión web evaluada en clase)

---

## Primera impresión
¿Qué entendí al entrar? ¿Qué me confundió?

- **¿Qué entendí al entrar?:**  
  Al ingresar a la aplicación se comprende que es una plataforma orientada a la organización colaborativa de eventos y reuniones grupales ("Planazo" / "Mis planes"), donde se listan los eventos creados, su organizador, la fecha límite de votación y su estado (Cancelado, Confirmado, Pendiente).

- **¿Qué me confundió?:**  
  - **[Funcionalidad 2 - Registro/Login]:** Al entrar a "Crear cuenta" o "Iniciar sesión", los campos de contraseña están completamente enmascarados con puntos y no disponen de ningún botón o icono de ojo para alternar su visibilidad. Si uno se equivoca de tecla, no sabe en qué carácter falló.
  - **[Funcionalidad 1 - Planes/Buscador]:** En la lista de planes, el buscador indica de forma genérica `"Buscar por nombre"`, dejando en duda si busca por nombre del plan o por nombre del organizador.
  - **[General]:** Al hacer scroll hacia abajo en la pantalla, el menú superior (*headerbar*) se pierde y desaparece de la vista, obligando a subir de nuevo hasta arriba para poder navegar o ver el usuario activo.

---

## Funcionalidad asignada y resultado
Describir la tarea indicada por el docente.

### 📌 Funcionalidad 1 (Asignada por el docente)
**Descripción de la tarea:**  
Crear un plan, agregar 2 opciones (propuestas de fecha/lugar) y votar por una de ellas.

**Marcar solo una opción:**
- [ ] La completé sin ayuda.
- [x] La completé con ayuda. ¿Cuál?  
  *Detalle de la ayuda:* Pude crear el plan con el botón `+ Crear plan`. Sin embargo, para agregar las 2 opciones y votar tuve problemas porque no sabía cómo hacerlo ni dónde presionar; no había un botón explícito de "Ver sala" o "Gestionar opciones". Al final resultó que debía apretar directamente sobre el mismo texto del nombre del plan en la tabla para ingresar a la sala y votar. Requerí ayuda y orientación para descubrir esa interacción oculta.
- [ ] No pude completarla. ¿Dónde me detuve?

---

### 📌 Funcionalidad 2 (Elegida por mí)
**Descripción de la tarea:**  
Flujo de autenticación de usuario: Probar el registro de una nueva cuenta ("Crear cuenta") e inicio de sesión ("Login").

**Marcar solo una opción:**
- [x] La completé sin ayuda.  
  *Detalle:* Pude completar el llenado del formulario de registro con nombre, correo y contraseñas, así como el inicio de sesión. No obstante, existió una fricción importante de usabilidad: no hay forma de visualizar las contraseñas escritas para comprobarlas antes de enviar los datos.
- [ ] La completé con ayuda. ¿Cuál?
- [ ] No pude completarla. ¿Dónde me detuve?

---

## Qué no funcionó
Pasos, resultado esperado y resultado observado.  
Si todo funcionó, indicarlo. Adjuntar captura si ayuda.

### 🔹 Respecto a la Funcionalidad 1 (Asignada por el docente: Planes y Votación)
1. **Selector de fecha y hora sin botón para confirmar:**
   - **Pasos:** En el modal *"Proponer nueva opción"*, seleccionar "Fecha y hora" e interactuar con el calendario y selector de hora desplegable.
   - **Resultado esperado:** Que el componente cuente con un botón de **"Aceptar"** o **"Confirmar"** para aplicar la selección y cerrar el calendario con claridad.
   - **Resultado observado:** Solo muestra "Borrar" y "Hoy", pero ningún botón para aceptar o cerrar la fecha elegida, generando incertidumbre de si la opción quedó guardada.
2. **Falta de affordance para entrar a las opciones y votación del plan:**
   - **Pasos:** Crear un nuevo plan y buscar cómo entrar a gestionarlo en la tabla de "Mis planes".
   - **Resultado esperado:** Que exista un botón visible en la columna "Acciones" (ej. "Ver sala", "Opciones" o "Votar") o que el nombre del plan tenga aspecto visual de enlace clickeable.
   - **Resultado observado:** En la columna "Acciones" solo aparecían "Confirmar/Cancelar", "Editar" y "Eliminar". No había indicación de que el texto del nombre del plan era el acceso a la sala.

### 🔹 Respecto a la Funcionalidad 2 (Elegida por mí: Registro y Login)
1. **Ausencia de opción para ver contraseña (Toggle de visibilidad):**
   - **Pasos:**
     1. Entrar a la pantalla de **"Crear cuenta"**.
     2. Llenar Nombre (`juan`), Correo (`juan@gmail.com`), Contraseña y Confirmar contraseña.
     3. Si ocurre una equivocación al tipear en alguno de los dos campos de contraseña (ocultos por defecto con puntos `••••••••`), intentar revisar en qué carácter estuvo el error.
     4. Luego ir a **"Iniciar sesión"**, ingresar correo y contraseña.
   - **Resultado esperado:**
     Tener un botón o icono de ojo (*mostrar/ocultar contraseña*) a la derecha de los campos de contraseña para poder inspeccionar visualmente lo escrito y corroborar que ambas coincidan y cumplan con los 8 caracteres requeridos.
   - **Resultado observado:**
     No hay ninguna opción ni botón para ver la contraseña ni en el registro ni en el login. Si el usuario se equivoca al escribir, no puede ver en dónde fue el error, viéndose forzado a borrar todo el campo a ciegas y volver a escribirlo desde cero.

---

## Qué mejoraría y por qué
Una propuesta concreta relacionada con la experiencia.

### 🔹 Para la Funcionalidad 1 (Asignada por el docente)
1. **Headerbar fijo (*Sticky Header*):** Mantener la barra superior de navegación fija al hacer scroll hacia abajo para no perder el acceso al menú principal, historial y perfil *(Heurística H3: Control y libertad del usuario)*.
2. **Especificar criterio en el buscador:** Cambiar el placeholder `"Buscar por nombre"` por `"Buscar por nombre del plan..."` o agregar un selector para definir si se busca por plan o por organizador *(Heurística H2: Correspondencia con el mundo real)*.
3. **Botón de confirmación en el calendario:** Agregar el botón "Aceptar" en el selector desplegable de fecha y hora *(Heurística H1: Visibilidad del estado del sistema)*.
4. **Botón explícito de sala/votación:** Agregar en la columna "Acciones" el botón "Ver sala" o "Votar" en los planes pendientes para que el usuario no tenga que adivinar que el nombre del plan es clickeable.

### 🔹 Para la Funcionalidad 2 (Elegida por mí)
1. **Botón para ver/ocultar contraseñas (Toggle Password Visibility):**  
   Incorporar un icono interactivo de ojo dentro de los campos de contraseña (tanto en *"Contraseña"* y *"Confirmar contraseña"* del Registro, como en el campo de contraseña del *Login*).  
   *Por qué:* Aplica directamente la **Heurística H5 (Prevención de errores)** y la **Heurística H9 (Ayudar a los usuarios a reconocer y recuperarse de errores)**. Al ser una contraseña de al menos 8 caracteres, es sumamente habitual cometer errores de tipeo. Poder ver la contraseña antes de enviar evita frustraciones, reduce intentos fallidos y agiliza el flujo de acceso.

---

## Qué quitaría y por qué
Si no quitaría nada, explicar por qué.

- **[Funcionalidad 1 - Edición de plan]:**  
  **Quitar la imagen/icono gigante del organizador al querer editar un plan.**  
  *Por qué:* Al abrir la ventana modal de *Editar plan*, aparece una silueta de usuario de tamaño desproporcionadamente grande que domina casi toda la tarjeta. Tiene un aspecto visual poco atractivo y empuja innecesariamente hacia abajo los campos de entrada relevantes (nombre del plan, organizador, fecha límite y botones de acción). Reemplazarlo por un avatar pequeño o un texto estilizado cumple con la **Heurística H8 (Diseño estético y minimalista)** y aprovecha mejor el espacio.
