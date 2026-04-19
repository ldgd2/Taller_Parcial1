class LoginRequest {
  final String username;
  final String password;

  LoginRequest({required this.username, required this.password});

  /// Convierte el objeto a JSON para el envío. 
  /// Usamos la convención del backend (username/password de OAuth2 o custom body).
  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'password': password,
    };
  }
}
