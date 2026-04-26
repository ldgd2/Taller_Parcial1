import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../data/vehicle_service.dart';

class VehicleListController extends ChangeNotifier {
  List<Map<String, dynamic>> vehicles = [];
  bool isLoading = false;
  late final VehicleService _vehicleService;

  VehicleListController() {
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    _vehicleService = VehicleService(apiClient: apiClient);
    loadVehicles();
  }

  Future<void> loadVehicles() async {
    isLoading = true;
    notifyListeners();

    try {
      vehicles = await _vehicleService.getMyVehicles();
    } catch (e) {
      debugPrint('Error loading vehicles: $e');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }

  // TODO: Implementar registro de vehículo
  Future<void> registerVehicle(String placa, String marca, String modelo, int anio) async {
    isLoading = true;
    notifyListeners();

    try {
      await _vehicleService.registerVehicle(
        placa: placa,
        marca: marca,
        modelo: modelo,
        anio: anio,
      );
      await loadVehicles(); // Recargar lista
    } catch (e) {
      debugPrint('Error registering vehicle: $e');
      rethrow;
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
