import 'package:go_router/go_router.dart';
import 'package:presupuesto_estudiantil/global/initial_route.dart';
import 'package:supabase_flutter/supabase_flutter.dart'; // <--- Importante
import '../screens/home_screen.dart';
import '../screens/login_screen.dart';
import '../screens/register_screen.dart';
import '../screens/movements_screen.dart';
import '../screens/history_screen.dart';
import '../screens/change_password_screen.dart';
import '../screens/reset_password_screen.dart';
import '../screens/presupuesto_categoria_screen.dart';

final privateRoutes = [
  '/movements',
  '/change-password',
  '/history',
  '/presupuestos-categoria',
];
final publicRoutes = ['/', '/login', '/register', '/reset-password'];

final appRouter = GoRouter(
  initialLocation: initialRoute,
  redirect: (context, state) {
    final sesion = Supabase.instance.client.auth.currentSession;
    String sigRuta = state.matchedLocation;

    if (sesion == null && privateRoutes.contains(sigRuta)) {
      return '/login';
    }
    return null;
  },
  routes: [
    GoRoute(path: '/', builder: (context, state) => const HomeScreen()),
    GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
    GoRoute(
      path: '/register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/change-password',
      builder: (context, state) => const ChangePasswordScreen(),
    ),
    GoRoute(
      path: '/movements',
      builder: (context, state) => const MovementsScreen(),
    ),
    /// Define una nueva ruta de navegación para el presupuesto mensual por categoría
    GoRoute(
      /// Indica la dirección de la ruta o URL a la que se navegará
      path: '/presupuestos-categoria',
      /// Función constructora que recibe context y state, y retorna la pantalla visual const PresupuestoCategoriaScreen
      builder: (context, state) => const PresupuestoCategoriaScreen(),
    ),
    GoRoute(
      path: '/history',
      builder: (context, state) => const HistoryScreen(),
    ),
    GoRoute(
      path: '/reset-password',
      builder: (context, state) => const ResetPasswordScreen(),
    ),
  ],
);
