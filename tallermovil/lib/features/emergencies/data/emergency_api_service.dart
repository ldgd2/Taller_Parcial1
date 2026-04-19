import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';

class EmergencyApiService {
  final ApiClient apiClient;

  EmergencyApiService({required this.apiClient});

  /// Sube evidencias y audio de forma simultánea. Retorna la transcripción si hay un audio.
  Future<Map<String, dynamic>> uploadMultimedia(List<String> filePaths) async {
    try {
      // Mapear rutas locales a objetos MultipartFile asíncronamente
      List<MultipartFile> multipartFiles = await Future.wait(
        filePaths.map((path) => MultipartFile.fromFile(path)),
      );

      FormData formData = FormData.fromMap({
        "files": multipartFiles,
      });

      final response = await apiClient.dio.post(
        '/emergencias/upload-multimedia',
        data: formData,
        options: Options(
           contentType: 'multipart/form-data',
        ),
      );

      return response.data; // { archivos: [...], transcripcion_cruda: "..." }
    } catch (e) {
      throw Exception('Fallo al subir archivos multimedia: $e');
    }
  }

  /// Registra la emergencia enviandos los datos y las urls de multimedia recolectadas.
  Future<Map<String, dynamic>> reportarEmergencia(Map<String, dynamic> data) async {
    try {
      final response = await apiClient.dio.post(
        '/emergencias/reportar',
        data: data,
      );
      return response.data;
    } catch (e) {
      throw Exception('Error al reportar emergencia: $e');
    }
  }
}
