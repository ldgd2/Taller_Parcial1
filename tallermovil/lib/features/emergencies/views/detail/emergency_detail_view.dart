import 'dart:io';
import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:path_provider/path_provider.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/feedback/t_badge.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/loaders/t_loader.dart';
import '../../../payments/views/payment_selection_view.dart';

class EmergencyDetailView extends StatefulWidget {
  final Map<String, dynamic> emergency;

  const EmergencyDetailView({super.key, required this.emergency});

  @override
  State<EmergencyDetailView> createState() => _EmergencyDetailViewState();
}

class _EmergencyDetailViewState extends State<EmergencyDetailView> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool isPlaying = false;

  Map<String, dynamic> _emergencyData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _emergencyData = widget.emergency;
    _audioPlayer.onPlayerStateChanged.listen((state) {
      if (mounted) {
        setState(() {
          isPlaying = state == PlayerState.playing;
        });
      }
    });
    _refreshData();
  }

  Future<void> _refreshData() async {
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      final response = await apiClient.dio.get('/emergencias/${widget.emergency['id']}');
      if (mounted) {
        setState(() {
          _emergencyData = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error refreshing emergency: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  String _fixUrl(String? url) {
    if (url == null) return '';
    if (url.startsWith('http')) return url;
    // Si la URL empieza con / la quitamos para no duplicar
    final cleanPath = url.startsWith('/') ? url.substring(1) : url;
    return '${ApiClient.serverUrl}/$cleanPath';
  }

  Future<void> _toggleAudio() async {
    final audioUrl = widget.emergency['audio_url'];
    if (audioUrl == null) return;

    final absoluteUrl = _fixUrl(audioUrl);
    debugPrint('Preparando audio: $absoluteUrl');

    try {
      if (isPlaying) {
        await _audioPlayer.stop();
        return;
      }

      // Estrategia: Descargar a temporal y reproducir (Más robusto que streaming HTTP en Android)
      final tempDir = await getTemporaryDirectory();
      final fileName = absoluteUrl.split('/').last;
      final file = File('${tempDir.path}/$fileName');

      if (!await file.exists()) {
        debugPrint('Descargando audio...');
        final storage = LocalStorage();
        final apiClient = ApiClient(localStorage: storage);
        await apiClient.dio.download(absoluteUrl, file.path);
        debugPrint('Descarga completada: ${file.path}');
      }

      await _audioPlayer.play(DeviceFileSource(file.path));
    } catch (e) {
      debugPrint('Error al procesar audio: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('No se pudo reproducir el audio: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Cargando...')),
        body: const Center(child: TLoader()),
      );
    }

    final e = _emergencyData;
    final resIA = e['resumen_ia'];
    final vehiculo = e['vehiculo'];
    final lat = e['latitud'] as double?;
    final lng = e['longitud'] as double?;

    return Scaffold(
      appBar: AppBar(
        title: TText.h3('Detalle de Emergencia'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Encabezado de Estado
            TCard(
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TText.h2('Estado Actual'),
                      _buildStatusBadge(e['estado_actual'] ?? 'PENDIENTE'),
                    ],
                  ),
                  TSpacing.verticalSmall(),
                  TText.body('Reportado el ${e['fecha']} a las ${e['hora']}'),
                ],
              ),
            ),
            TSpacing.verticalLarge(),

            // SECCIÓN DE PAGO (Solo si está finalizado y TIENE MONTO)
            if ((['ATENDIDO', 'FINALIZADA'].contains(e['estado_actual']?.toString().toUpperCase()) || e['idPago'] != null) && (e['monto_pago'] ?? e['pago']?['monto']) != null) ...[
              TText.h3('Pago del Servicio'),
              TSpacing.verticalSmall(),
              TCard(
                color: AppColors.successBg.withValues(alpha: 0.2),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        TText.body('Monto Total a Pagar:'),
                        TText.h2('\$${e['monto_pago'] ?? e['pago']?['monto'] ?? '--.--'}'),
                      ],
                    ),
                    TSpacing.verticalSmall(),
                    if (e['pago']?['estado'] == 'COMPLETADO') ...[
                      const Icon(Icons.check_circle, color: AppColors.success, size: 48),
                      TSpacing.verticalSmall(),
                      TText.h3('SERVICIO PAGADO'),
                      TText.body('El pago se realizó correctamente.'),
                    ] else ...[
                      TText.label('El servicio ha finalizado. Por favor, procede al pago.'),
                      TSpacing.verticalMedium(),
                      _PaymentButton(emergency: e),
                    ],
                  ],
                ),
              ),
              TSpacing.verticalLarge(),
            ],

            // Información del Vehículo
            TText.h3('Vehículo Afectado'),
            TSpacing.verticalSmall(),
            TCard(
              child: Row(
                children: [
                  const Icon(Icons.directions_car, color: AppColors.primary, size: 32),
                  TSpacing.horizontalMedium(),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        TText.h3(vehiculo != null ? '${vehiculo['marca']} ${vehiculo['modelo']}' : 'N/A'),
                        TText.label('Placa: ${e['placaVehiculo']}'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            TSpacing.verticalLarge(),

            // Descripción y Multimedia
            TText.h3('Evidencia Enviada'),
            TSpacing.verticalSmall(),
            TCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TText.body(e['descripcion'] ?? ''),
                  if (e['audio_url'] != null) ...[
                    TSpacing.verticalMedium(),
                    TButton(
                      label: isPlaying ? 'Detener Audio' : 'Escuchar mi Reporte',
                      icon: isPlaying ? Icons.stop : Icons.play_arrow,
                      onPressed: _toggleAudio,
                      variant: TButtonVariant.outline,
                    ),
                  ],
                  if (e['evidencias'] != null && (e['evidencias'] as List).isNotEmpty) ...[
                    TSpacing.verticalMedium(),
                    TText.label('Fotos adjuntas:'),
                    TSpacing.verticalSmall(),
                    SizedBox(
                      height: 100,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: (e['evidencias'] as List).length,
                        itemBuilder: (context, index) {
                          final imgUrl = _fixUrl(e['evidencias'][index]['direccion']);
                          return Container(
                            margin: const EdgeInsets.only(right: 8),
                            width: 100,
                            decoration: BoxDecoration(
                              color: AppColors.neutral100,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.network(
                                imgUrl,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ),
            TSpacing.verticalLarge(),

            // Minimapa
            if (lat != null && lng != null) ...[
              TText.h3('Ubicación del Reporte'),
              TSpacing.verticalSmall(),
              TCard(
                padding: 0,
                child: Column(
                  children: [
                    SizedBox(
                      height: 200,
                      child: ClipRRect(
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
                        child: FlutterMap(
                          options: MapOptions(
                            initialCenter: LatLng(lat, lng),
                            initialZoom: 15.0,
                          ),
                          children: [
                            TileLayer(
                              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                              userAgentPackageName: 'com.example.tallermovil',
                            ),
                            MarkerLayer(
                              markers: [
                                Marker(
                                  point: LatLng(lat, lng),
                                  width: 40,
                                  height: 40,
                                  child: const Icon(Icons.location_on, color: AppColors.danger, size: 40),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          const Icon(Icons.map_outlined, size: 16, color: AppColors.textMuted),
                          TSpacing.horizontalSmall(),
                          Expanded(child: TText.label(e['direccion'] ?? 'Ubicación GPS')),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              TSpacing.verticalLarge(),
            ],

            // Resumen IA (Si existe)
            if (resIA != null) ...[
              TText.h3('Análisis Inteligente (IA)'),
              TSpacing.verticalSmall(),
              TCard(
                color: AppColors.primary900.withValues(alpha: 0.2),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome, color: AppColors.primary, size: 20),
                        TSpacing.horizontalSmall(),
                        TText.h3('Diagnóstico Preliminar'),
                      ],
                    ),
                    TSpacing.verticalSmall(),
                    TText.body(resIA['resumen'] ?? 'Analizando...'),
                  ],
                ),
              ),
            ],
            TSpacing.verticalXLarge(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    switch (status.toUpperCase()) {
      case 'PENDIENTE':
        return TBadge.warning('Pendiente');
      case 'ASIGNADO':
        return TBadge.info('Asignado');
      case 'EN PROCESO':
        return TBadge.info('En Proceso');
      case 'FINALIZADA':
      case 'COMPLETADO':
      case 'ATENDIDO':
        return TBadge.success('Finalizado');
      case 'CANCELADO':
        return TBadge.error('Cancelado');
      default:
        return TBadge.info(status);
    }
  }
}

class _PaymentButton extends StatefulWidget {
  final Map<String, dynamic> emergency;
  const _PaymentButton({required this.emergency});

  @override
  State<_PaymentButton> createState() => _PaymentButtonState();
}

class _PaymentButtonState extends State<_PaymentButton> {
  bool _isPaying = false;

  @override
  Widget build(BuildContext context) {
    final e = widget.emergency;
    return TButton(
      label: 'Pagar ahora con Stripe',
      icon: Icons.payment,
      isLoading: _isPaying,
      onPressed: _isPaying ? null : () async {
        final montoStr = e['monto_pago'] ?? e['pago']?['monto'] ?? '0';
        final double monto = double.tryParse(montoStr.toString()) ?? 0.0;
        
        if (monto <= 0) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('El monto debe ser mayor a 0')),
          );
          return;
        }

        setState(() => _isPaying = true);
        try {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => PaymentSelectionView(
                emergenciaId: e['id'],
                monto: monto,
              ),
            ),
          );

          if (result == true && mounted) {
            Navigator.pop(context, true); 
          }
        } finally {
          if (mounted) setState(() => _isPaying = false);
        }
      },
      variant: TButtonVariant.primary,
    );
  }
}
