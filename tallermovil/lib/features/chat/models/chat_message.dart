class ChatMessage {
  final int id;
  final int idEmergencia;
  final int remitenteId;
  final String rolRemitente;
  final String? contenido;
  final String? imagenUrl;
  final String? audioUrl;
  final DateTime fechaEnvio;

  ChatMessage({
    required this.id,
    required this.idEmergencia,
    required this.remitenteId,
    required this.rolRemitente,
    this.contenido,
    this.imagenUrl,
    this.audioUrl,
    required this.fechaEnvio,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      idEmergencia: json['idEmergencia'],
      remitenteId: json['remitente_id'],
      rolRemitente: json['rol_remitente'],
      contenido: json['contenido'],
      imagenUrl: json['imagen_url'],
      audioUrl: json['audio_url'],
      fechaEnvio: DateTime.parse(json['fecha_envio']),
    );
  }
}
