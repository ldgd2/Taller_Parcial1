import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../data/emergency_service.dart';

class EmergencyHistoryController extends ChangeNotifier {
  List<Map<String, dynamic>> emergencies = [];
  bool isLoading = false;
  late final EmergencyService _emergencyService;

  EmergencyHistoryController() {
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    _emergencyService = EmergencyService(apiClient: apiClient);
    loadHistory();
  }

  Future<void> loadHistory() async {
    isLoading = true;
    notifyListeners();

    try {
      emergencies = await _emergencyService.getHistory();
    } catch (e) {
      debugPrint('Error loading emergency history: $e');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
