class AuthResponse {
  final String accessToken;
  final String tokenType;
  final String rol;
  final String? taller;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.rol,
    this.taller,
  });

  /// Inicializa el objeto a partir del JSON devuelto por el backend.
  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String,
      rol: json['rol'] as String,
      taller: json['taller'] as String?,
    );
  }
}
