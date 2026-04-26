import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/components/buttons/t_button.dart';
import '../../../shared/components/inputs/t_text_input.dart';
import '../../../shared/components/layout/t_spacing.dart';
import '../../../shared/components/layout/t_list_tile.dart';
import '../../../shared/components/typography/t_text.dart';
import '../../../shared/components/loaders/t_loader.dart';
import 'vehicle_list_controller.dart';

class VehicleSettingsScreen extends StatefulWidget {
  const VehicleSettingsScreen({super.key});

  @override
  State<VehicleSettingsScreen> createState() => _VehicleSettingsScreenState();
}

class _VehicleSettingsScreenState extends State<VehicleSettingsScreen> {
  late final VehicleListController controller;

  @override
  void initState() {
    super.initState();
    controller = VehicleListController();
  }

  void _showAddVehicleModal() {
    final placaController = TextEditingController();
    final marcaController = TextEditingController();
    final modeloController = TextEditingController();
    final anioController = TextEditingController();

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
                TText.h2('Agregar Vehículo'),
                TSpacing.verticalLarge(),
                TTextInput(
                  label: 'Placa', 
                  hint: 'Ej: 4501-BDF',
                  controller: placaController,
                ),
                TSpacing.verticalMedium(),
                TTextInput(
                  label: 'Marca', 
                  hint: 'Ej: Nissan',
                  controller: marcaController,
                ),
                TSpacing.verticalMedium(),
                TTextInput(
                  label: 'Modelo', 
                  hint: 'Ej: Sentra',
                  controller: modeloController,
                ),
                TSpacing.verticalMedium(),
                TTextInput(
                  label: 'Año', 
                  hint: 'Ej: 2021', 
                  keyboardType: TextInputType.number,
                  controller: anioController,
                ),
                TSpacing.verticalXLarge(),
                TButton(
                  label: 'Guardar Vehículo',
                  onPressed: () async {
                    if (placaController.text.isEmpty || marcaController.text.isEmpty) return;
                    
                    try {
                      await controller.registerVehicle(
                        placaController.text,
                        marcaController.text,
                        modeloController.text,
                        int.tryParse(anioController.text) ?? 2024,
                      );
                      if (mounted) {
                        Navigator.pop(context);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Vehículo registrado correctamente')),
                        );
                      }
                    } catch (e) {
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Error: $e')),
                        );
                      }
                    }
                  },
                ),
                TSpacing.verticalLarge(),
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
      appBar: AppBar(title: TText.h3('Mis Autos')),
      body: AnimatedBuilder(
        animation: controller,
        builder: (context, child) {
          if (controller.isLoading) {
            return const Center(child: TLoader());
          }

          return RefreshIndicator(
            onRefresh: controller.loadVehicles,
            child: ListView.separated(
              padding: const EdgeInsets.all(24.0),
              itemCount: controller.vehicles.length + 1,
              separatorBuilder: (context, index) => TSpacing.verticalMedium(),
              itemBuilder: (context, index) {
                if (index == controller.vehicles.length) {
                  return TButton(
                    label: 'Añadir Otro Vehículo',
                    icon: Icons.add,
                    variant: TButtonVariant.outline,
                    onPressed: _showAddVehicleModal,
                  );
                }
                final auto = controller.vehicles[index];
                return TListTile(
                  title: '${auto["marca"]} ${auto["modelo"]}',
                  subtitle: 'Placa: ${auto["placa"]}',
                  leading: const Icon(Icons.directions_car_outlined, color: AppColors.primary),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppColors.danger), 
                    onPressed: () {}
                  ),
                );
              },
            ),
          );
        }
      ),
    );
  }
}
