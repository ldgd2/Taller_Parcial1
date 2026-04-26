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

class ManageCardsView extends StatefulWidget {
  const ManageCardsView({super.key});

  @override
  State<ManageCardsView> createState() => _ManageCardsViewState();
}

class _ManageCardsViewState extends State<ManageCardsView> {
  bool _isLoading = true;
  List<dynamic> _cards = [];
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
    } catch (e) {
      debugPrint('Error al cargar tarjetas: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis Tarjetas')),
      body: _isLoading
          ? const Center(child: TLoader())
          : Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TText.h3('Tarjetas Registradas'),
                  TText.label('Gestiona tus métodos de pago para servicios de emergencia.', color: AppColors.textMuted),
                  TSpacing.verticalLarge(),
                  if (_cards.isEmpty)
                    Expanded(
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.credit_card_off_outlined, size: 64, color: AppColors.textMuted),
                            TSpacing.verticalMedium(),
                            TText.body('No tienes tarjetas guardadas'),
                            TSpacing.verticalLarge(),
                          ],
                        ),
                      ),
                    )
                  else
                    Expanded(
                      child: ListView.builder(
                        itemCount: _cards.length,
                        itemBuilder: (context, index) {
                          final card = _cards[index];
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12.0),
                            child: TCard(
                              child: Row(
                                children: [
                                  const Icon(Icons.credit_card, color: AppColors.primary),
                                  TSpacing.horizontalMedium(),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        TText.h3('${card['marca'].toString().toUpperCase()} **** ${card['ultimo4']}'),
                                        TText.label('Vencimiento: ${card['exp_month']}/${card['exp_year']}', color: AppColors.textMuted),
                                      ],
                                    ),
                                  ),
                                  const Icon(Icons.check_circle_outline, color: AppColors.success),
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
                    onPressed: () async {
                      final result = await Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const AddCardView()),
                      );
                      if (result == true) _loadCards();
                    },
                  ),
                  TSpacing.verticalLarge(),
                ],
              ),
            ),
    );
  }
}
