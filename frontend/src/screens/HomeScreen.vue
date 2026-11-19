<script setup>
// Pantalla de inicio (página pública). Diseño basado en el mockup de inicio:
// barra con logo, portada con la ilustración del estudiante y tres tarjetas de beneficios.
import { nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BarraPublica from '../widgets/BarraPublica.vue'
import ilustracion from '../assets/inicio/ilustracion-estudiante.jpg'
import iconoBilletera from '../assets/inicio/icono-billetera.png'
import iconoHistorial from '../assets/inicio/icono-historial.png'
import iconoCategorias from '../assets/inicio/icono-categorias.png'
import '../theme/paginasPublicas.css'

const router = useRouter()
const route = useRoute()

const beneficios = [
  {
    icono: iconoBilletera,
    titulo: 'Control de Gastos',
    texto: 'Anota tus gastos e ingresos y ponte un límite mensual para no pasarte.',
  },
  {
    icono: iconoHistorial,
    titulo: 'Historial de Movimientos',
    texto: 'Revisa qué registraste, qué cambiaste y cuándo lo hiciste.',
  },
  {
    icono: iconoCategorias,
    titulo: 'Gastos por Categorías',
    texto: 'Define cuánto quieres gastar en comida, transporte o estudios cada mes.',
  },
]

const pasos = [
  { titulo: 'Crea tu cuenta', texto: 'Solo necesitas tu correo y una contraseña.' },
  { titulo: 'Registra tus movimientos', texto: 'Cada gasto o ingreso en segundos, con su categoría.' },
  { titulo: 'Decide con claridad', texto: 'Mira cuánto te queda, ahorra para tus metas y evita sorpresas.' },
]

// Si llega desde otra página con /#beneficios, baja a esa sección
onMounted(async () => {
  if (route.hash) {
    await nextTick()
    document.querySelector(route.hash)?.scrollIntoView()
  }
})
</script>

<template>
  <div class="publico">
    <BarraPublica pagina="inicio" />

    <main>
      <section id="inicio" class="portada" aria-labelledby="titulo-portada">
        <div class="pub-contenedor portada-fila">
          <div class="portada-texto">
            <h1 id="titulo-portada" class="portada-titulo">Domina tus finanzas universitarias sin estrés</h1>
            <p class="portada-lema">
              Aprende a gestionar tu dinero, controlar gastos diarios y ahorrar para lo que realmente
              importa mientras estudias.
            </p>
            <div class="portada-botones">
              <button type="button" class="pub-btn pub-btn-primario portada-btn" @click="router.push('/register')">
                Comenzar Ahora
              </button>
              <a href="#como-funciona" class="pub-btn pub-btn-secundario portada-btn">
                Ver Cómo Funciona
                <svg width="14" height="16" viewBox="0 0 14 16" aria-hidden="true"><path d="M1 1 L13 8 L1 15 Z" fill="currentColor" /></svg>
              </a>
            </div>
          </div>
          <img class="portada-ilustracion-movil" :src="ilustracion" alt="" width="900" height="942" />
        </div>
      </section>

      <section id="beneficios" class="beneficios" aria-labelledby="titulo-beneficios">
        <h2 id="titulo-beneficios" class="visually-hidden">Beneficios</h2>
        <ul class="pub-contenedor beneficios-lista">
          <li v-for="b in beneficios" :key="b.titulo" class="beneficio">
            <img :src="b.icono" alt="" width="80" height="80" class="beneficio-icono" />
            <div>
              <h3 class="beneficio-titulo">{{ b.titulo }}</h3>
              <p class="beneficio-texto">{{ b.texto }}</p>
            </div>
          </li>
        </ul>
      </section>

      <section id="como-funciona" class="como-funciona" aria-labelledby="titulo-como-funciona">
        <div class="pub-contenedor">
          <h2 id="titulo-como-funciona" class="seccion-titulo">Cómo funciona</h2>
          <ol class="pasos">
            <li v-for="(p, i) in pasos" :key="p.titulo" class="paso">
              <span class="paso-numero" aria-hidden="true">{{ i + 1 }}</span>
              <h3 class="paso-titulo">{{ p.titulo }}</h3>
              <p class="paso-texto">{{ p.texto }}</p>
            </li>
          </ol>
          <div class="como-funciona-accion">
            <button type="button" class="pub-btn pub-btn-primario" @click="router.push('/register')">
              Empezar gratis
            </button>
          </div>
        </div>
      </section>
    </main>

    <footer class="pie">
      <div class="pub-contenedor">Presupuesto Estudiantil · Hecho para estudiantes</div>
    </footer>
  </div>
</template>

<style scoped>
/* ---------- Portada ---------- */
.portada {
  position: relative;
  display: flex;
  align-items: center;
  min-height: clamp(560px, 50vw, 720px);
  padding: 48px 0 140px;
  background: url('../assets/inicio/fondo-inicio.jpg') right 30% / cover no-repeat, var(--degradado-publico);
}

.portada-texto {
  max-width: 680px;
}

.portada-titulo {
  color: var(--color-publico-titulo);
  font-size: clamp(34px, 3.7vw, 56px);
  font-weight: 700;
  line-height: 1.12;
  letter-spacing: -0.5px;
}

.portada-lema {
  max-width: 580px;
  margin-top: 20px;
  color: var(--color-publico-texto);
  font-size: clamp(17px, 1.6vw, 21px);
  line-height: 1.55;
}

.portada-botones {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 36px;
}

.portada-btn {
  min-height: 56px;
  padding: 12px 34px;
  font-size: 19px;
}

.portada-ilustracion-movil {
  display: none;
}

/* ---------- Beneficios: tarjetas montadas sobre el borde de la portada ---------- */
.beneficios {
  position: relative;
  margin-top: -96px;
}

.beneficios-lista {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
  margin: 0 auto;
  list-style: none;
}

.beneficio {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 22px 26px;
  border-radius: var(--radio-tarjeta-publica);
  background: var(--color-superficie);
  box-shadow: var(--sombra-publica);
}

.beneficio-icono {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
}

.beneficio-titulo {
  color: var(--color-publico-titulo);
  font-size: 21px;
  font-weight: 500;
  line-height: 1.25;
}

.beneficio-texto {
  margin-top: 4px;
  color: var(--color-publico-texto-suave);
  font-size: 15px;
  line-height: 1.45;
}

/* ---------- Cómo funciona ---------- */
.como-funciona {
  padding: 72px 0 64px;
}

.seccion-titulo {
  color: var(--color-publico-titulo);
  font-size: 32px;
  font-weight: 700;
  text-align: center;
}

.pasos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
  margin: 36px 0 0;
  padding: 0;
  list-style: none;
}

.paso {
  padding: 28px;
  border: 1px solid var(--color-publico-borde-tarjeta);
  border-radius: var(--radio-tarjeta-publica);
  background: var(--color-publico-tarjeta-suave);
}

.paso-numero {
  display: inline-grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-publico-icono-fondo);
  color: var(--color-publico-accion);
  font-size: 20px;
  font-weight: 700;
}

.paso-titulo {
  margin-top: 14px;
  color: var(--color-publico-titulo);
  font-size: 20px;
  font-weight: 700;
}

.paso-texto {
  margin-top: 6px;
  color: var(--color-publico-texto-suave);
}

.como-funciona-accion {
  display: flex;
  justify-content: center;
  margin-top: 36px;
}

.pie {
  padding: 24px 0;
  border-top: 1px solid var(--color-publico-separador);
  color: var(--color-publico-texto-suave);
  font-size: 14px;
  text-align: center;
}

/* ---------- Pantallas angostas: texto arriba e ilustración abajo ---------- */
@media (max-width: 900px) {
  .portada {
    min-height: 0;
    padding: 40px 0 120px;
    background: var(--degradado-publico);
  }

  .portada-texto {
    max-width: none;
  }

  .portada-ilustracion-movil {
    display: block;
    width: 100%;
    max-width: 460px;
    height: auto;
    margin: 32px auto 0;
    border-radius: 24px;
  }

  .beneficios-lista,
  .pasos {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 560px) {
  .portada-botones {
    flex-direction: column;
  }

  .portada-btn {
    width: 100%;
  }
}
</style>
