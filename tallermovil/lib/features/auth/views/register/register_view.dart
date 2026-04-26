import 'package:flutter/material.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/inputs/t_text_input.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/layouts/form_page_layout.dart';
import 'register_controller.dart';

class RegisterView extends StatefulWidget {
  const RegisterView({super.key});

  @override
  State<RegisterView> createState() => _RegisterViewState();
}

class _RegisterViewState extends State<RegisterView> {
  late final RegisterController controller;

  @override
  void initState() {
    super.initState();
    controller = RegisterController();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        return FormPageLayout(
          title: "Crear Cuenta",
          formKey: controller.formKey,
          body: Column(
            children: [
              TSpacing.verticalLarge(),
              TText.body('Completa tus datos para empezar a recibir asistencia técnica S.O.S.'),
              TSpacing.verticalLarge(),
              
              TCard(
                title: "Información Personal",
                child: Column(
                  children: [
                    TTextInput(
                      label: "Nombre Completo",
                      controller: controller.nombreController,
                      validator: (val) => val != null && val.isNotEmpty ? null : 'Nombre requerido',
                    ),
                    TTextInput(
                      label: "Correo Electrónico",
                      controller: controller.correoController,
                      keyboardType: TextInputType.emailAddress,
                      validator: (val) => val != null && val.contains('@') ? null : 'Correo inválido',
                    ),
                    TTextInput(
                      label: "Contraseña",
                      isPassword: true,
                      controller: controller.contrasenaController,
                      validator: (val) => val != null && val.length >= 6 ? null : 'Mínimo 6 caracteres',
                    ),
                  ],
                ),
              ),
              
              TSpacing.verticalLarge(),
              
              TCard(
                title: "Tu Primer Vehículo",
                child: Column(
                  children: [
                    TTextInput(
                      label: "Placa / Patente",
                      hint: "Ej: ABC-123",
                      controller: controller.placaController,
                      validator: (val) => val != null && val.isNotEmpty ? null : 'Placa requerida',
                    ),
                    Row(
                      children: [
                        Expanded(
                          child: TTextInput(
                            label: "Marca",
                            hint: "Ej: Toyota",
                            controller: controller.marcaController,
                            validator: (val) => val != null && val.isNotEmpty ? null : 'Requerido',
                          ),
                        ),
                        TSpacing.horizontalMedium(),
                        Expanded(
                          child: TTextInput(
                            label: "Año",
                            hint: "2024",
                            keyboardType: TextInputType.number,
                            controller: controller.anioController,
                            validator: (val) => val != null && val.isNotEmpty ? null : 'Requerido',
                          ),
                        ),
                      ],
                    ),
                    TTextInput(
                      label: "Modelo",
                      hint: "Ej: Hilux",
                      controller: controller.modeloController,
                      validator: (val) => val != null && val.isNotEmpty ? null : 'Requerido',
                    ),
                  ],
                ),
              ),
              
              TSpacing.verticalXLarge(),
              
              TButton(
                label: "Finalizar Registro",
                onPressed: () => controller.register(context),
                isLoading: controller.isLoading,
                icon: Icons.check_circle_outline,
              ),
              
              TSpacing.verticalLarge(),
            ],
          ),
        );
      },
    );
  }
}
