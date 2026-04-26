import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';

class LocationService {
  /// Solicita permisos de ubicación al usuario y obtiene las coordenadas actuales.
  static Future<Position> getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    // 1. Verifica si el GPS está prendido en el celular
    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Los servicios de ubicación están deshabilitados. Encienda su GPS.');
    }

    // 2. Verifica permisos
    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Permisos de ubicación fueron denegados.');
      }
    }
    
    if (permission == LocationPermission.deniedForever) {
      throw Exception('Los permisos de ubicación fueron denegados permanentemente.');
    } 

    // 3. Obtiene la posición (Precisión Alta)
    return await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.bestForNavigation,
        ),
    );
  }

  /// Convierte coordenadas Lat/Lng en una dirección legible por humanos (Reverse Geocoding)
  static Future<String> getAddressFromLatLng(double lat, double lng) async {
    try {
      List<Placemark> placemarks = await placemarkFromCoordinates(lat, lng);
      
      if (placemarks.isNotEmpty) {
        Placemark place = placemarks[0];
        
        // Construimos una dirección amigable
        // Ejemplo: Calle Bolivar 123, Ciudad, País
        final List<String> parts = [];
        if (place.street != null && place.street!.isNotEmpty) parts.add(place.street!);
        if (place.locality != null && place.locality!.isNotEmpty) parts.add(place.locality!);
        if (place.country != null && place.country!.isNotEmpty) parts.add(place.country!);
        
        return parts.join(', ');
      }
      return 'Dirección no encontrada';
    } catch (e) {
      return 'Error al obtener dirección: $e';
    }
  }
}
