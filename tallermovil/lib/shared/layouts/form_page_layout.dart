import 'package:flutter/material.dart';

/// FormPageLayout: Layout estándar para pantallas de tipo formulario.
/// Maneja automáticamente:
/// 1. El Scaffold y AppBar (con botón atrás nativo).
/// 2. El SingleChildScrollView para que el teclado no oculte los inputs.
/// 3. Un GestureDetector para cerrar el teclado al tocar fuera.
/// 4. Padding global y SafeArea.
class FormPageLayout extends StatelessWidget {
  /// Título en el AppBar
  final String title;

  /// Contenido principal (generalmente un Column con campos TTextInput)
  final Widget body;

  /// Opcional: Widgets a la derecha del AppBar (acciones)
  final List<Widget>? actions;

  /// Padding de la página, por defecto 24.
  final double padding;

  /// Identificador para el formulario (si se envuelve en Form)
  final Key? formKey;

  const FormPageLayout({
    super.key,
    required this.title,
    required this.body,
    this.actions,
    this.padding = 24.0,
    this.formKey,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      // Ocultar teclado al tocar fuera de un input
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: AppBar(
          title: Text(title),
          actions: actions,
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(padding),
            child: Form(
              key: formKey,
              child: body,
            ),
          ),
        ),
      ),
    );
  }
}
