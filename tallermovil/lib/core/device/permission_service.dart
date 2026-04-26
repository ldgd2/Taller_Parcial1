import 'package:permission_handler/permission_handler.dart';

class PermissionService {
  /// Solicita todos los permisos necesarios para el funcionamiento de la app
  static Future<void> requestAllPermissions() async {
    await [
      Permission.camera,
      Permission.microphone,
      Permission.location,
      Permission.notification,
      Permission.storage,
      // Para Android 13+ (Opcional, pero recomendado)
      Permission.photos,
      Permission.audio,
    ].request();
  }

  static Future<bool> hasCameraPermission() async => await Permission.camera.isGranted;
  static Future<bool> hasMicPermission() async => await Permission.microphone.isGranted;
  static Future<bool> hasLocationPermission() async => await Permission.location.isGranted;
}
