import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/loaders/t_loader.dart';
import '../../../../shared/components/buttons/t_button.dart';

class PaymentSimulatorView extends StatefulWidget {
  final int emergenciaId;

  const PaymentSimulatorView({super.key, required this.emergenciaId});

  @override
  State<PaymentSimulatorView> createState() => _PaymentSimulatorViewState();
}

class _PaymentSimulatorViewState extends State<PaymentSimulatorView> {
  bool isLoading = true;
  Map<String, dynamic>? simulation;

  @override
  void initState() {
    super.initState();
    _loadSimulation();
  }

  Future<void> _loadSimulation() async {
    setState(() => isLoading = true);
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      final response = await apiClient.dio.post('/pagos/simular/${widget.emergenciaId}');
      setState(() {
        simulation = response.data;
        isLoading = false;
      });
    } catch (e) {
      debugPrint('Error simulation: $e');
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: TText.h3('Simulador de Pago (IA)')),
      body: isLoading
          ? const Center(child: TLoader())
          : simulation == null
              ? Center(child: TText.body('No se pudo generar la simulación.'))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      TText.h2('Presupuesto Estimado'),
                      TText.label('Generado por nuestra IA experta', color: AppColors.primary),
                      TSpacing.verticalLarge(),
                      
                      TCard(
                        child: Column(
                          children: [
                            _buildRow('Mano de Obra', '\$${simulation!['mano_de_obra']}'),
                            const Divider(height: 32),
                            TText.label('Repuestos Estimados', color: AppColors.textMuted),
                            TSpacing.verticalSmall(),
                            ...(simulation!['repuestos_estimados'] as List).map((item) {
                              return _buildRow(item['item'], '\$${item['costo']}', isSmall: true);
                            }),
                            const Divider(height: 32),
                            _buildRow('Comisión Sistema (10%)', '\$${simulation!['comision_sistema']}', color: AppColors.success),
                            TSpacing.verticalMedium(),
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: AppColors.primary.withValues(alpha: 0.1),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: _buildRow('TOTAL APROXIMADO', '\$${simulation!['total_estimado']}', isBold: true),
                            ),
                          ],
                        ),
                      ),
                      TSpacing.verticalLarge(),
                      
                      TText.h3('Justificación Técnica'),
                      TSpacing.verticalSmall(),
                      TCard(
                        color: AppColors.neutral100,
                        child: TText.body(simulation!['justificacion_mercado']),
                      ),
                      TSpacing.verticalXLarge(),
                      
                      TButton(
                        label: 'Entendido',
                        onPressed: () => Navigator.pop(context),
                      ),
                      TSpacing.verticalLarge(),
                    ],
                  ),
                ),
    );
  }

  Widget _buildRow(String label, String value, {bool isBold = false, bool isSmall = false, Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: isSmall 
              ? TText.label(label) 
              : isBold ? TText.h3(label) : TText.body(label),
          ),
          isBold 
            ? TText.h3(value, color: color ?? AppColors.textPrimary) 
            : TText.body(value, color: color ?? AppColors.textPrimary),
        ],
      ),
    );
  }
}
