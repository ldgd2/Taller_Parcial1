import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/components/cards/t_card.dart';
import '../../../shared/components/layout/t_spacing.dart';
import '../../../shared/components/typography/t_text.dart';
import '../../../shared/components/buttons/t_button.dart';
import '../../../shared/components/loaders/t_loader.dart';
import '../services/payment_service.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/local_storage.dart';
import 'add_card_view.dart';

class PaymentSelectionView extends StatefulWidget {
  final int emergenciaId;
  final double monto;

  const PaymentSelectionView({
    super.key,
    required this.emergenciaId,
    required this.monto,
  });

  @override
  State<PaymentSelectionView> createState() => _PaymentSelectionViewState();
}

class _PaymentSelectionViewState extends State<PaymentSelectionView> {
  bool _isLoading = true;
  bool _isProcessingPayment = false;
  List<dynamic> _cards = [];
  String? _selectedCardId;
  late final PaymentService _paymentService;

  @override
  void initState() {
    super.initState();
    _paymentService = PaymentService(
      apiClient: ApiClient(localStorage: LocalStorage()),
    );
    _loadCards();
  }

  Future<void> _loadCards() async {
    setState(() => _isLoading = true);
    try {
      _cards = await _paymentService.getSavedCards();
      if (_cards.isNotEmpty) {
        _selectedCardId = _cards[0]['stripe_payment_method_id'];
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _processPayment() async {
    if (_selectedCardId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, selecciona una tarjeta')),
      );
      return;
    }

    setState(() => _isProcessingPayment = true);
    try {
      final success = await _paymentService.payEmergency(
        emergenciaId: widget.emergenciaId,
        monto: widget.monto,
        metodoPagoId: _selectedCardId,
      );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('¡Pago completado con éxito!')),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error en el pago: $e'), backgroundColor: AppColors.danger),
        );
      }
    } finally {
      if (mounted) setState(() => _isProcessingPayment = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Completar Pago')),
      body: _isLoading
          ? const Center(child: TLoader())
          : Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TText.h3('Monto a Pagar: \$${widget.monto.toStringAsFixed(2)}'),
                  TText.label('Incluye comisión de plataforma (10%)', color: AppColors.textMuted),
                  TSpacing.verticalLarge(),
                  TText.h3('Selecciona una Tarjeta'),
                  TSpacing.verticalSmall(),
                  if (_cards.isEmpty)
                    Center(
                      child: Column(
                        children: [
                          TSpacing.verticalLarge(),
                          const Icon(Icons.credit_card_off_outlined, size: 48, color: AppColors.textMuted),
                          TSpacing.verticalMedium(),
                          TText.body('No tienes tarjetas guardadas'),
                        ],
                      ),
                    )
                  else
                    Expanded(
                      child: ListView.builder(
                        itemCount: _cards.length,
                        itemBuilder: (context, index) {
                          final card = _cards[index];
                          final isSelected = _selectedCardId == card['stripe_payment_method_id'];
                          
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12.0),
                            child: TCard(
                              onTap: () => setState(() => _selectedCardId = card['stripe_payment_method_id']),
                              child: Row(
                                children: [
                                  Icon(
                                    card['marca'].toString().toLowerCase().contains('visa') 
                                      ? Icons.credit_card 
                                      : Icons.credit_card,
                                    color: isSelected ? AppColors.primary : AppColors.textMuted,
                                  ),
                                  TSpacing.horizontalMedium(),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        TText.h3('${card['marca'].toString().toUpperCase()} **** ${card['ultimo4']}'),
                                      ],
                                    ),
                                  ),
                                  if (isSelected)
                                    const Icon(Icons.check_circle, color: AppColors.success),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  TButton(
                    label: 'Añadir Nueva Tarjeta',
                    icon: Icons.add,
                    variant: TButtonVariant.secondary,
                    onPressed: () async {
                      final result = await Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const AddCardView()),
                      );
                      if (result == true) _loadCards();
                    },
                  ),
                  TSpacing.verticalMedium(),
                  TButton(
                    label: 'Pagar Ahora',
                    icon: Icons.payment,
                    isLoading: _isProcessingPayment,
                    onPressed: _cards.isEmpty ? null : _processPayment,
                  ),
                ],
              ),
            ),
    );
  }
}
