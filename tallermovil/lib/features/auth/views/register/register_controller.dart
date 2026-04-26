import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../shared/components/feedback/t_snackbar.dart';
import '../../data/auth_api_service.dart';
import '../../data/auth_repository.dart';
import '../../models/register_request.dart';

class RegisterController extends ChangeNotifier {
  final nombreController = TextEditingController();
  final correoController = TextEditingController();
  final contrasenaController = TextEditingController();
  
  // Datos del Vehículo
  final placaController = TextEditingController();
  final marcaController = TextEditingController();
  final modeloController = TextEditingController();
  final anioController = TextEditingController();

  final formKey = GlobalKey<FormState>();
  bool isLoading = false;

  late final AuthRepository _repository;

  RegisterController() {
    // Inicialización simple para demostración (Beginner friendly)
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    final apiService = AuthApiService(apiClient: apiClient);
    _repository = AuthRepository(apiService: apiService, localStorage: storage);
  }

  @override
  void dispose() {
    nombreController.dispose();
    correoController.dispose();
    contrasenaController.dispose();
    placaController.dispose();
    marcaController.dispose();
    modeloController.dispose();
    anioController.dispose();
    super.dispose();
  }

  Future<void> register(BuildContext context) async {
    if (formKey.currentState?.validate() ?? false) {
      isLoading = true;
      notifyListeners();

      try {
        final request = RegisterRequest(
          nombre: nombreController.text.trim(),
          correo: correoController.text.trim(),
          contrasena: contrasenaController.text,
          vehiculo: VehiculoRegisterRequest(
            placa: placaController.text.trim().toUpperCase(),
            marca: marcaController.text.trim(),
            modelo: modeloController.text.trim(),
            anio: int.tryParse(anioController.text) ?? 2024,
          ),
        );

        await _repository.register(request);

        if (!context.mounted) return;
        
        TSnackbar.success(context, '¡Cuenta creada con éxito! Ahora puedes iniciar sesión.');
        Navigator.pop(context); // Volver al Login
      } catch (e) {
        if (!context.mounted) return;
        TSnackbar.error(context, e.toString());
      } finally {
        isLoading = false;
        notifyListeners();
      }
    }
  }
}
