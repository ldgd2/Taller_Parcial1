import 'package:flutter/material.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/inputs/t_text_input.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/layouts/form_page_layout.dart';
import '../register/register_view.dart';
import 'login_controller.dart';

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  late final LoginController controller;

  @override
  void initState() {
    super.initState();
    controller = LoginController();
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
          title: "Bienvenido",
          formKey: controller.formKey,
          body: Column(
            children: [
              TSpacing.verticalXLarge(),
              // Logo
              Icon(
                Icons.directions_car, 
                size: 80, 
                color: Theme.of(context).colorScheme.primary
              ),
              TSpacing.verticalLarge(),
              
              TCard(
                title: "Inicia Sesión",
                child: Column(
                  children: [
                    TTextInput(
                      label: "Correo Electrónico",
                      hint: "ejemplo@taller.com",
                      prefixIcon: Icons.email_outlined,
                      keyboardType: TextInputType.emailAddress,
                      controller: controller.emailController,
                      validator: (val) => val != null && val.contains('@') ? null : 'Correo inválido',
                    ),
                    TTextInput(
                      label: "Contraseña",
                      prefixIcon: Icons.lock_outline,
                      isPassword: true,
                      controller: controller.passwordController,
                      validator: (val) => val != null && val.length >= 6 ? null : 'Mínimo 6 caracteres',
                    ),
                    TSpacing.verticalMedium(),
                    TButton(
                      label: "Ingresar al Sistema",
                      onPressed: () => controller.login(context),
                      isLoading: controller.isLoading,
                      icon: Icons.login,
                    ),
                    TSpacing.verticalMedium(),
                    TButton(
                      label: "Olvidé mi contraseña",
                      onPressed: controller.resetPassword,
                      variant: TButtonVariant.text,
                    ),
                  ],
                ),
              ),
              
              TSpacing.verticalXLarge(),
              TButton(
                label: "Crear Nueva Cuenta",
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const RegisterView()),
                  );
                },
                variant: TButtonVariant.outline,
              ),
            ],
          ),
        );
      },
    );
  }
}
