import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../models/login_request.dart';
import '../models/auth_response.dart';
import '../models/register_request.dart';

class AuthApiService {
  final ApiClient apiClient;

  AuthApiService({required this.apiClient});

  /// Ejecuta la llamada POST a /auth/login
  Future<AuthResponse> login(LoginRequest request) async {
    try {
      // El backend espera JSON con correo, contrasena y rol
      final response = await apiClient.dio.post(
        '/auth/login',
        data: request.toJson(),
      );

      return AuthResponse.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('Credenciales inválidas');
      }
      final message = e.response?.data?['detail'] ?? 'Error al iniciar sesión';
      throw Exception(message);
    } catch (e) {
      throw Exception('Ocurrió un error inesperado al iniciar sesión');
    }
  }

  /// Ejecuta la llamada POST a /clientes/registro
  Future<void> register(RegisterRequest request) async {
    try {
      await apiClient.dio.post(
        '/clientes/registro',
        data: request.toJson(),
      );
    } on DioException catch (e) {
      final message = e.response?.data?['detail'] ?? 'Error al registrarse';
      throw Exception(message);
    } catch (e) {
      throw Exception('Ocurrió un error inesperado al registrarse');
    }
  }

  /// Ejecuta la llamada POST a /auth/logout (opcional, si el backend lo requiere)
  Future<void> logout() async {
    try {
      await apiClient.dio.post('/auth/logout');
    } catch (e) {
      // Ignorar el error del servidor al hacer logout local
    }
  }
}
