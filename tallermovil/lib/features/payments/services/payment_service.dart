import 'package:flutter_stripe/flutter_stripe.dart';
import '../../../core/network/api_client.dart';

class PaymentService {
  final ApiClient apiClient;

  PaymentService({required this.apiClient});

  /// 1. Registrar una nueva tarjeta
  Future<void> registerCard() async {
    try {
      // Pedir SetupIntent al backend
      final response = await apiClient.dio.post('/pagos/stripe/setup-intent');
      final clientSecret = response.data['client_secret'];
      final customerId = response.data['customer_id'];

      // Mostrar el formulario de Stripe para la tarjeta
      await Stripe.instance.initPaymentSheet(
        paymentSheetParameters: SetupPaymentSheetParameters(
          setupIntentClientSecret: clientSecret,
          customerId: customerId,
          merchantDisplayName: 'Taller Móvil',
        ),
      );

      // Presentar la hoja de pago
      await Stripe.instance.presentPaymentSheet();

      // Sincronizar con el backend para que guarde el nuevo PM en nuestra DB
      await apiClient.dio.post('/pagos/stripe/sync-cards');
      
    } catch (e) {
      rethrow;
    }
  }

  /// 2. Pagar una emergencia
  Future<bool> payEmergency({
    required int emergenciaId,
    required double monto,
    String? metodoPagoId,
  }) async {
    try {
      // Crear PaymentIntent en el backend
      final response = await apiClient.dio.post('/pagos/stripe/create-intent', data: {
        'emergencia_id': emergenciaId,
        'monto': monto,
        'metodo_pago_id': metodoPagoId,
      });

      final String status = response.data['estado'];
      
      // Si el pago ya se completó (ej: usamos una tarjeta guardada off-session)
      if (status == 'COMPLETADO') {
        return true;
      }

      // Si no, podríamos necesitar confirmación adicional (3DSecure)
      // Pero por ahora lo dejamos así para el flujo básico.
      return status == 'COMPLETADO';
      
    } catch (e) {
      rethrow;
    }
  }

  /// 3. Listar tarjetas
  Future<List<dynamic>> getSavedCards() async {
    try {
      final response = await apiClient.dio.get('/pagos/stripe/metodos');
      return response.data;
    } catch (e) {
      return [];
    }
  }
}
