import 'package:intl/intl.dart';

class EmergencyReport {
  final String descripcion;
  final String direccion;
  final double latitud;
  final double longitud;
  final String placaVehiculo;
  final String? audioUrl;
  final List<String> evidenciasUrls;
  final String? textoAdicional;

  EmergencyReport({
    required this.descripcion,
    required this.direccion,
    required this.latitud,
    required this.longitud,
    required this.placaVehiculo,
    this.audioUrl,
    this.evidenciasUrls = const [],
    this.textoAdicional,
  });

  Map<String, dynamic> toJson() {
    return {
      'descripcion': descripcion,
      'direccion': direccion,
      'latitud': latitud,
      'longitud': longitud,
      'placaVehiculo': placaVehiculo,
      'audio_url': audioUrl,
      'evidencias_urls': evidenciasUrls,
      'texto_adicional': textoAdicional,
      'hora': DateFormat('HH:mm:ss').format(DateTime.now()),
    };
  }
}
