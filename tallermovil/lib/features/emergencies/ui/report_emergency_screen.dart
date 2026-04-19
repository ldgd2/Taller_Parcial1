import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:uuid/uuid.dart';

import '../../../core/device/location_service.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../shared/widgets/primary_button.dart';
import '../../../shared/widgets/custom_text_field.dart';
import '../../../shared/widgets/glass_card.dart';

class ReportEmergencyScreen extends StatefulWidget {
  const ReportEmergencyScreen({super.key});

  @override
  State<ReportEmergencyScreen> createState() => _ReportEmergencyScreenState();
}

class _ReportEmergencyScreenState extends State<ReportEmergencyScreen> {
  // Grabadora
  late final AudioRecorder _audioRecorder;
  bool _isRecording = false;
  String? _audioPath;

  // Temporizador 2 Minutos
  Timer? _timer;
  int _recordDuration = 0; // en segundos
  final int _maxDuration = 120; // 2 minutos

  // Evidencias (Fotos)
  final ImagePicker _picker = ImagePicker();
  final List<String> _imagePaths = [];

  // Formulario
  final TextEditingController _placaController = TextEditingController();
  final TextEditingController _descripcionController = TextEditingController();

  bool _isUploading = false;

  @override
  void initState() {
    super.initState();
    _audioRecorder = AudioRecorder();
    _checkPermissions();
  }

  @override
  void dispose() {
    _timer?.cancel();
    _audioRecorder.dispose();
    _placaController.dispose();
    _descripcionController.dispose();
    super.dispose();
  }

  Future<void> _checkPermissions() async {
    await [
      Permission.microphone,
      Permission.camera,
    ].request();
  }

  void _startTimer() {
    _recordDuration = 0;
    _timer = Timer.periodic(const Duration(seconds: 1), (Timer t) {
      setState(() => _recordDuration++);
      if (_recordDuration >= _maxDuration) {
        _stopRecording(); // Corte bruto al min 2:00
      }
    });
  }

  String _formatNumber(int number) {
    String numberStr = number.toString();
    if (number < 10) return '0$numberStr';
    return numberStr;
  }

  Future<void> _startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final dir = await getApplicationDocumentsDirectory();
        final path = '${dir.path}/audio_${const Uuid().v4()}.m4a';

        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.aacLc), 
          path: path
        );

        setState(() {
          _isRecording = true;
          _audioPath = null;
        });
        _startTimer();
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Permiso de micrófono denegado.')),
        );
      }
    } catch (e) {
      debugPrint('Error al iniciar grabación: $e');
    }
  }

  Future<void> _stopRecording() async {
    try {
      _timer?.cancel();
      final path = await _audioRecorder.stop();
      
      setState(() {
        _isRecording = false;
        if (path != null) _audioPath = path;
      });
    } catch (e) {
      debugPrint('Error al detener grabación: $e');
    }
  }

  Future<void> _pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      setState(() {
        _imagePaths.add(image.path);
      });
    }
  }



  @override
  Widget build(BuildContext context) {
    String minutes = _formatNumber(_recordDuration ~/ 60);
    String seconds = _formatNumber(_recordDuration % 60);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Reportar Emergencia'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Por favor, describe oralmente el problema del vehículo o sube evidencias. Tienes un máximo de 2 MINUTOS.',
              style: AppTextStyles.bodyMedium,
            ),
            const SizedBox(height: 24),

            // Contenedor Grabadora
            GlassCard(
              child: Column(
                children: [
                   Text(
                    '$minutes:$seconds',
                    style: AppTextStyles.h1.copyWith(
                      color: _isRecording ? AppColors.error : AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  GestureDetector(
                    onTap: _isRecording ? _stopRecording : _startRecording,
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: _isRecording ? AppColors.error : AppColors.primary,
                        shape: BoxShape.circle,
                        boxShadow: _isRecording ? [
                          BoxShadow(color: AppColors.error.withAlpha(128), blurRadius: 20, spreadRadius: 5)
                        ] : [],
                      ),
                      child: Icon(
                        _isRecording ? Icons.stop : Icons.mic,
                        color: Colors.white,
                        size: 40,
                      ),
                    ).animate(target: _isRecording ? 1 : 0).scale(begin: const Offset(1,1), end: const Offset(1.1,1.1)),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _isRecording ? 'Grabando...' : (_audioPath != null ? 'Audio listo para enviar' : 'Toque para grabar'),
                    style: AppTextStyles.label,
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),

            // Selector Multi-media
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Evidencias Visuales', style: AppTextStyles.h3),
                IconButton(
                  icon: const Icon(Icons.add_a_photo, color: AppColors.primary),
                  onPressed: _pickImage,
                ),
              ],
            ),
            const SizedBox(height: 8),
            
            // Carrusel horizontal de imágenes
            if (_imagePaths.isNotEmpty)
              SizedBox(
                height: 80,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _imagePaths.length,
                  itemBuilder: (context, index) {
                    return Container(
                      margin: const EdgeInsets.only(right: 8),
                      width: 80,
                      decoration: BoxDecoration(
                        color: AppColors.surfaceLight,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Center(child: Icon(Icons.image, color: AppColors.textMuted)),
                      // Nota ideal: Usar Image.file(File(_imagePaths[index]))
                    );
                  },
                ),
              ),

            const SizedBox(height: 24),

            // Formulario final (Selección de Vehículo)
            Text('Vehículo Afectado', style: AppTextStyles.label),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                hintText: 'Selecciona tu vehículo',
              ),
              dropdownColor: AppColors.surfaceLight,
              items: const [
                DropdownMenuItem(value: 'ABC-123', child: Text('Audi Q5 (ABC-123)')),
                DropdownMenuItem(value: 'XYZ-987', child: Text('Toyota Hilux (XYZ-987)')),
              ], // TODO: Cargar desde API del perfil del cliente
              onChanged: (val) {},
            ),

            const SizedBox(height: 16),
            const CustomTextField(
              label: 'Descripción (Si no puede hablar)',
              hint: 'Ej: Choque frontal',
            ),

            const SizedBox(height: 32),

            PrimaryButton(
              text: 'Obtener GPS y Generar Reporte',
              icon: Icons.satellite_alt_outlined,
              isLoading: _isUploading,
              onPressed: (_audioPath != null || _imagePaths.isNotEmpty) ? () async {
                setState(() => _isUploading = true);
                try {
                  // 1. Extraemos GPS automáticamente y estrictamente (Requisito vital)
                  final position = await LocationService.getCurrentLocation();
                  
                  // 2. Aquí llamaríamos a API Service: await _submitEmergency(...)
                  await Future.delayed(const Duration(seconds: 1)); // Simula red
                  
                  if (!mounted) {
                    return;
                  }
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('S.O.S Enviado. Lat: ${position.latitude.toStringAsFixed(4)}, Lng: ${position.longitude.toStringAsFixed(4)}'),
                      backgroundColor: AppColors.success,
                    ),
                  );
                  Navigator.pop(context); // Volver al home

                } catch (e) {
                  if (!mounted) {
                     return;
                  }
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString()), backgroundColor: AppColors.error));
                } finally {
                  if (mounted) {
                    setState(() => _isUploading = false);
                  }
                }
              } : null,
            ),
          ],
        ),
      ),
    );
  }
}

