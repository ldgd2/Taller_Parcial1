import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/components/cards/t_card.dart';
import '../../../shared/components/layout/t_spacing.dart';
import '../../../shared/components/typography/t_text.dart';
import '../../../shared/components/buttons/t_button.dart';
import '../services/payment_service.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/local_storage.dart';

class AddCardView extends StatefulWidget {
  const AddCardView({super.key});

  @override
  State<AddCardView> createState() => _AddCardViewState();
}

class _AddCardViewState extends State<AddCardView> {
  bool _isLoading = false;
  late final PaymentService _paymentService;

  @override
  void initState() {
    super.initState();
    _paymentService = PaymentService(
      apiClient: ApiClient(localStorage: LocalStorage()),
    );
  }

  Future<void> _registerCard() async {
    setState(() => _isLoading = true);
    try {
      await _paymentService.registerCard();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('¡Tarjeta registrada exitosamente!')),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al registrar tarjeta: $e'), backgroundColor: AppColors.danger),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registrar Tarjeta')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TCard(
              child: Column(
                children: [
                  const Icon(Icons.credit_card_outlined, size: 64, color: AppColors.primary),
                  TSpacing.verticalMedium(),
                  TText.h3('Pago Seguro con Stripe'),
                  TText.body(
                    'Registra tu tarjeta para realizar pagos rápidos en tus emergencias.',
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
            const Spacer(),
            TButton(
              label: 'Añadir Tarjeta',
              icon: Icons.add,
              isLoading: _isLoading,
              onPressed: _registerCard,
            ),
            TSpacing.verticalLarge(),
          ],
        ),
      ),
    );
  }
}
