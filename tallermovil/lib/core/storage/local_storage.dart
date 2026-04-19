import 'package:shared_preferences/shared_preferences.dart';

/// Wrappea SharedPreferences para manejar la sesión persistente (similar al localStorage web).
class LocalStorage {
  static const String _keyToken = 'access_token';
  static const String _keyCodTaller = 'cod_taller';
  static const String _keyRol = 'rol';

  // --- Token ---
  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyToken, token);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyToken);
  }

  // --- Datos de Sesión (Taller, Rol) ---
  Future<void> saveSessionData({required String codTaller, required String rol}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyCodTaller, codTaller);
    await prefs.setString(_keyRol, rol);
  }

  Future<String?> getCodTaller() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyCodTaller);
  }

  Future<String?> getRol() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyRol);
  }

  // --- Limpieza ---
  Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    // Limpiamos las llaves específicas de sesión
    await prefs.remove(_keyToken);
    await prefs.remove(_keyCodTaller);
    await prefs.remove(_keyRol);
  }
}
