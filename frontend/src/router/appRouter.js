// Portado de lib/router/app_router.dart
import { createRouter, createWebHistory } from 'vue-router'
import { sesionActual } from '../services/sesion.js'
import HomeScreen from '../screens/HomeScreen.vue'
import LoginScreen from '../screens/LoginScreen.vue'
import RegisterScreen from '../screens/RegisterScreen.vue'
import MovementsScreen from '../screens/MovementsScreen.vue'
import HistoryScreen from '../screens/HistoryScreen.vue'
import ChangePasswordScreen from '../screens/ChangePasswordScreen.vue'
import ResetPasswordScreen from '../screens/ResetPasswordScreen.vue'
import PresupuestoCategoriaScreen from '../screens/PresupuestoCategoriaScreen.vue'
import MetasScreen from '../screens/MetasScreen.vue'
import AnaliticaScreen from '../screens/AnaliticaScreen.vue'

export const privateRoutes = [
  '/movements',
  '/change-password',
  '/history',
  '/presupuestos-categoria',
  '/metas',
  '/analitica',
]
export const publicRoutes = ['/', '/login', '/register', '/reset-password']

export const appRouter = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeScreen },
    { path: '/login', component: LoginScreen },
    { path: '/register', component: RegisterScreen },
    { path: '/change-password', component: ChangePasswordScreen },
    { path: '/movements', component: MovementsScreen },
    /// Ruta de navegación para el presupuesto mensual por categoría
    { path: '/presupuestos-categoria', component: PresupuestoCategoriaScreen },
    /// Ruta de navegación para metas de ahorro y fondos disponibles (Tarea 8)
    { path: '/metas', component: MetasScreen },
    /// Clase 21: panel propio de analítica (solo desarrollo)
    { path: '/analitica', component: AnaliticaScreen },
    { path: '/history', component: HistoryScreen },
    { path: '/reset-password', component: ResetPasswordScreen },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

// Sin sesion no se puede entrar a las rutas privadas
appRouter.beforeEach((to) => {
  const sesion = sesionActual.value
  if (sesion === null && privateRoutes.includes(to.path)) {
    return '/login'
  }
  return true
})
