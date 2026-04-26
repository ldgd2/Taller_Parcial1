import 'package:flutter/material.dart';
import '../../../shared/layouts/form_page_layout.dart';
import '../../../shared/components/buttons/t_button.dart';
import '../../../shared/components/cards/t_card.dart';
import '../../../shared/components/inputs/t_text_input.dart';
// import '../data/auth_repository.dart'; // Si lo necesitas en el futuro

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // En C# usaríamos propiedades o Bindings. Aquí usamos Controllers.
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  bool _isLoading = false;

  void _onLoginClick() async {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() => _isLoading = true);
      
      // Simulando llamada a la API (C# async Task)
      await Future.delayed(const Duration(seconds: 2));
      
      if (mounted) {
        setState(() => _isLoading = false);
        // Aquí iría la navegación a MainNavigationScreen
        // Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const MainNavigationScreen()));
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('¡Inicio de sesión exitoso!')),
        );
      }
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Usamos FormPageLayout (nuestra plantilla tipo Window de C#)
    return FormPageLayout(
      title: "Bienvenido",
      formKey: _formKey,
      body: Column(
        children: [
          const SizedBox(height: 40),
          // Logo (Simulado)
          Icon(Icons.directions_car, size: 80, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 24),
          
          // Agrupamos el formulario en nuestra TCard (Como un GroupBox en WinForms)
          TCard(
            title: "Inicia Sesión",
            child: Column(
              children: [
                TTextInput(
                  label: "Correo Electrónico",
                  hint: "ejemplo@taller.com",
                  prefixIcon: Icons.email_outlined,
                  keyboardType: TextInputType.emailAddress,
                  controller: _emailController,
                  validator: (val) => val != null && val.contains('@') ? null : 'Correo inválido',
                ),
                TTextInput(
                  label: "Contraseña",
                  prefixIcon: Icons.lock_outline,
                  isPassword: true,
                  controller: _passwordController,
                  validator: (val) => val != null && val.length >= 6 ? null : 'Mínimo 6 caracteres',
                ),
                const SizedBox(height: 16),
                TButton(
                  label: "Ingresar al Sistema",
                  onPressed: _onLoginClick,
                  isLoading: _isLoading,
                  icon: Icons.login,
                ),
                const SizedBox(height: 16),
                TButton(
                  label: "Olvidé mi contraseña",
                  onPressed: () {},
                  variant: TButtonVariant.text,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 30),
          TButton(
            label: "Crear Nueva Cuenta",
            onPressed: () {},
            variant: TButtonVariant.outline,
          ),
        ],
      ),
    );
  }
}
