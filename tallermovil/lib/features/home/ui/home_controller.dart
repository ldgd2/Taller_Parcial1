import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../vehicles/data/vehicle_service.dart';

class HomeController extends ChangeNotifier {
  List<Map<String, dynamic>> vehicles = [];
  bool isLoading = false;
  late final VehicleService _vehicleService;

  HomeController() {
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    _vehicleService = VehicleService(apiClient: apiClient);
    loadData();
  }

  Future<void> loadData() async {
    isLoading = true;
    notifyListeners();

    try {
      vehicles = await _vehicleService.getMyVehicles();
    } catch (e) {
      debugPrint('Error loading home data: $e');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
