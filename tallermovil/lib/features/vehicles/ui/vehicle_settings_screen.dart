import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/primary_button.dart';
import '../../../shared/widgets/custom_text_field.dart';

class VehicleSettingsScreen extends StatefulWidget {
  const VehicleSettingsScreen({super.key});

  @override
  State<VehicleSettingsScreen> createState() => _VehicleSettingsScreenState();
}

class _VehicleSettingsScreenState extends State<VehicleSettingsScreen> {
  // Simulamos datos de vehículos para la UI base (Luego vendrá del endpoint)
  final List<Map<String, String>> _vehiculos = [
    {"placa": "ABC-123", "marca": "Audi", "modelo": "Q5"},
    {"placa": "XYZ-987", "marca": "Toyota", "modelo": "Hilux"},
  ];

  void _showAddVehicleModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.background,
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(
             bottom: MediaQuery.of(context).viewInsets.bottom,
             left: 24, right: 24, top: 24,
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Agregar Vehículo', style: AppTextStyles.h2),
                const SizedBox(height: 24),
                const CustomTextField(label: 'Placa', hint: 'Ej: 4501-BDF'),
                const SizedBox(height: 16),
                const CustomTextField(label: 'Marca', hint: 'Ej: Nissan'),
                const SizedBox(height: 16),
                const CustomTextField(label: 'Modelo', hint: 'Ej: Sentra'),
                const SizedBox(height: 16),
                const CustomTextField(label: 'Año', hint: 'Ej: 2021', keyboardType: TextInputType.number),
                const SizedBox(height: 32),
                PrimaryButton(
                  text: 'Guardar Vehículo',
                  onPressed: () {
                    Navigator.pop(context); // TODO: Llamar Endpoint POST
                  },
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        );
      }
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis Autos')),
      body: ListView.separated(
        padding: const EdgeInsets.all(24.0),
        itemCount: _vehiculos.length + 1, // +1 para el botón añadir
        separatorBuilder: (context, index) => const SizedBox(height: 16),
        itemBuilder: (context, index) {
          if (index == _vehiculos.length) {
            return OutlinedButton.icon(
              onPressed: _showAddVehicleModal,
              icon: const Icon(Icons.add, color: AppColors.primary),
              label: const Text('Añadir Otro Vehículo'),
            );
          }
          final auto = _vehiculos[index];
          return GlassCard(
            child: Row(
              children: [
                const Icon(Icons.directions_car_outlined, size: 40, color: AppColors.primary),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('${auto["marca"]} ${auto["modelo"]}', style: AppTextStyles.h3),
                      Text('Placa: ${auto["placa"]}', style: AppTextStyles.bodyMedium),
                    ],
                  ),
                ),
                IconButton(icon: const Icon(Icons.delete_outline, color: AppColors.error), onPressed: (){})
              ],
            ),
          );
        },
      ),
    );
  }
}
