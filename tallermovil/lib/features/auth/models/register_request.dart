class RegisterRequest {
  final String nombre;
  final String correo;
  final String contrasena;
  final VehiculoRegisterRequest vehiculo;

  RegisterRequest({
    required this.nombre,
    required this.correo,
    required this.contrasena,
    required this.vehiculo,
  });

  Map<String, dynamic> toJson() => {
        'nombre': nombre,
        'correo': correo,
        'contrasena': contrasena,
        'vehiculo': vehiculo.toJson(),
      };
}

class VehiculoRegisterRequest {
  final String placa;
  final String marca;
  final String modelo;
  final int anio;

  VehiculoRegisterRequest({
    required this.placa,
    required this.marca,
    required this.modelo,
    required this.anio,
  });

  Map<String, dynamic> toJson() => {
        'placa': placa,
        'marca': marca,
        'modelo': modelo,
        'anio': anio,
      };
}
