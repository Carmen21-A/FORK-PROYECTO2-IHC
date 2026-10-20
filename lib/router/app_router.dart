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

final privateRoutes = ['/movements', '/change-password', '/history'];
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
