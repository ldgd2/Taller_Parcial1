import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../models/login_request.dart';
import '../models/auth_response.dart';

class AuthApiService {
  final ApiClient apiClient;

  AuthApiService({required this.apiClient});

  /// Ejecuta la llamada POST a /auth/login
  Future<AuthResponse> login(LoginRequest request) async {
    try {
      // El backend FastAPI espera Content-Type: application/x-www-form-urlencoded
      // para los endpoints de OAuth2PasswordRequestForm, a menos que se haya cambiado
      // Aquí usamos Form-Data porque típicamente oauth2 de FastAPI lo requiere.
      final response = await apiClient.dio.post(
        '/auth/login',
        data: {
          'username': request.username,
          'password': request.password,
        },
        options: Options(
          contentType: Headers.formUrlEncodedContentType
        )
      );

      return AuthResponse.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('Credenciales inválias');
      }
      throw Exception('Error al conectar con el servidor: ${e.message}');
    } catch (e) {
      throw Exception('Ocurrió un error inesperado al iniciar sesión');
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
