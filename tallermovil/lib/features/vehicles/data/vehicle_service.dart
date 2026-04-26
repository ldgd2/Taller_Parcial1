import '../../../../core/network/api_client.dart';

class VehicleService {
  final ApiClient apiClient;

  VehicleService({required this.apiClient});

  /// Obtiene la lista de vehículos del cliente autenticado
  Future<List<Map<String, dynamic>>> getMyVehicles() async {
    try {
      final response = await apiClient.dio.get('/clientes/mis-vehiculos');
      return List<Map<String, dynamic>>.from(response.data);
    } catch (e) {
      throw Exception('Error al cargar vehículos');
    }
  }

  /// Registra un nuevo vehículo para el cliente
  Future<Map<String, dynamic>> registerVehicle({
    required String placa,
    required String marca,
    required String modelo,
    required int anio,
  }) async {
    try {
      final response = await apiClient.dio.post(
        '/clientes/vehiculos',
        data: {
          'placa': placa,
          'marca': marca,
          'modelo': modelo,
          'anio': anio,
        },
      );
      return response.data;
    } catch (e) {
      throw Exception('Error al registrar vehículo: $e');
    }
  }
}
