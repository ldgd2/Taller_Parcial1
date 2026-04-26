class LoginRequest {
  final String correo;
  final String contrasena;
  final String rol;

  LoginRequest({
    required this.correo,
    required this.contrasena,
    this.rol = 'cliente', // Por defecto cliente para la app móvil
  });

  Map<String, dynamic> toJson() {
    return {
      'correo': correo,
      'contrasena': contrasena,
      'rol': rol,
    };
  }
}
