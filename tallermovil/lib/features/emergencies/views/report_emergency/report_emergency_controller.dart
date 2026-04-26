import 'dart:async';
import 'package:flutter/material.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';
import '../../../../core/device/location_service.dart';
import '../../../../core/device/permission_service.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../shared/components/feedback/t_snackbar.dart';
import '../../../vehicles/data/vehicle_service.dart';
import 'emergency_upload_controller.dart';

class ReportEmergencyController extends ChangeNotifier {
  // Grabadora
  late final AudioRecorder _audioRecorder;
  bool isRecording = false;
  String? audioPath;

  // Reproductor
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool isPlaying = false;
  StreamSubscription? _audioSubscription;

  // Temporizador 2 Minutos
  Timer? _timer;
  int recordDuration = 0; // en segundos
  final int maxDuration = 120; // 2 minutos

  // Evidencias (Fotos)
  final ImagePicker _picker = ImagePicker();
  final List<String> imagePaths = [];

  // Formulario
  String placa = '';
  String descripcion = '';

  bool isUploading = false;
  late final VehicleService _vehicleService;
  List<Map<String, dynamic>> vehicles = [];
  
  int? editingEmergencyId;

  ReportEmergencyController({Map<String, dynamic>? existingEmergency}) {
    _audioRecorder = AudioRecorder();
    _checkPermissions();
    
    if (existingEmergency != null) {
      editingEmergencyId = existingEmergency['id'];
      descripcion = existingEmergency['descripcion'] ?? '';
      placa = existingEmergency['placaVehiculo'] ?? '';
      audioPath = existingEmergency['audio_url'];
      if (existingEmergency['evidencias'] != null) {
        for (var ev in existingEmergency['evidencias']) {
          imagePaths.add(ev['direccion']);
        }
      }
    }

    // Iniciar servicio
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    _vehicleService = VehicleService(apiClient: apiClient);

    _loadVehicles();

    // Listeners del reproductor
    _audioSubscription = _audioPlayer.onPlayerStateChanged.listen((state) {
      if (!isClosed) {
        isPlaying = state == PlayerState.playing;
        notifyListeners();
      }
    });
  }

  bool isClosed = false;

  @override
  void dispose() {
    isClosed = true;
    _timer?.cancel();
    _audioSubscription?.cancel();
    _audioRecorder.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _checkPermissions() async {
    await PermissionService.requestAllPermissions();
  }

  Future<void> _loadVehicles() async {
    try {
      vehicles = await _vehicleService.getMyVehicles();
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading vehicles for emergency: $e');
    }
  }

  void _startTimer() {
    recordDuration = 0;
    _timer = Timer.periodic(const Duration(seconds: 1), (Timer t) {
      recordDuration++;
      notifyListeners();
      if (recordDuration >= maxDuration) {
        stopRecording(); // Corte bruto al min 2:00
      }
    });
  }

  String formatTime(int number) {
    String numberStr = number.toString();
    if (number < 10) return '0$numberStr';
    return numberStr;
  }

  Future<void> startRecording(BuildContext context) async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final dir = await getApplicationDocumentsDirectory();
        final path = '${dir.path}/audio_${const Uuid().v4()}.m4a';

        await _audioRecorder.start(
          const RecordConfig(encoder: AudioEncoder.aacLc), 
          path: path
        );

        isRecording = true;
        audioPath = null;
        notifyListeners();
        _startTimer();
      } else {
        if (!context.mounted) return;
        TSnackbar.error(context, 'Permiso de micrófono denegado.');
      }
    } catch (e) {
      debugPrint('Error al iniciar grabación: $e');
    }
  }

  Future<void> stopRecording() async {
    try {
      _timer?.cancel();
      final path = await _audioRecorder.stop();
      
      isRecording = false;
      if (path != null) audioPath = path;
      notifyListeners();
    } catch (e) {
      debugPrint('Error al detener grabación: $e');
    }
  }

  Future<void> playRecording() async {
    if (audioPath != null) {
      if (isPlaying) {
        await _audioPlayer.stop();
      } else {
        await _audioPlayer.play(DeviceFileSource(audioPath!));
      }
    }
  }

  void clearAudio() {
    audioPath = null;
    notifyListeners();
  }

  Future<void> pickImage() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      imagePaths.add(image.path);
      notifyListeners();
    }
  }

  void setDescripcion(String val) {
    descripcion = val;
    notifyListeners();
  }

  void setPlaca(String val) {
    placa = val;
    notifyListeners();
  }

  Future<void> submitReport(BuildContext context) async {
    if (audioPath == null && imagePaths.isEmpty) {
      TSnackbar.error(context, 'Debes incluir al menos un audio o una foto.');
      return;
    }
    if (placa.isEmpty) {
      TSnackbar.error(context, 'Por favor selecciona un vehículo.');
      return;
    }

    try {
      TSnackbar.info(context, 'Obteniendo ubicación y enviando en segundo plano...');
      
      final position = await LocationService.getCurrentLocation();
      final address = await LocationService.getAddressFromLatLng(position.latitude, position.longitude);
      
      EmergencyUploadController().queueEmergency(
        audioPath: audioPath,
        imagePaths: List.from(imagePaths),
        placa: placa,
        descripcion: descripcion,
        latitude: position.latitude,
        longitude: position.longitude,
        address: address,
        existingEmergencyId: editingEmergencyId,
      );

      if (context.mounted) {
        Navigator.pop(context);
      }

    } catch (e) {
      if (context.mounted) {
        TSnackbar.error(context, 'Error al obtener ubicación: $e');
      }
    }
  }
}
