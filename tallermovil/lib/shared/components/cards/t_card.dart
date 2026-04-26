import 'package:flutter/material.dart';

/// TCard: Contenedor tipo Tarjeta estándar de la aplicación.
/// Mantiene bordes, padding y diseño visual coherente de manera automática.
class TCard extends StatelessWidget {
  /// Contenido principal de la tarjeta
  final Widget child;

  /// Título opcional superior
  final String? title;

  /// Relleno interno (Padding). Por defecto es 20.
  final double padding;

  /// Margen externo.
  final EdgeInsetsGeometry? margin;

  /// Acción al presionar la tarjeta
  final VoidCallback? onTap;

  /// Color de fondo personalizado
  final Color? color;

  const TCard({
    super.key,
    required this.child,
    this.title,
    this.padding = 20.0,
    this.margin,
    this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Card(
        color: color,
        margin: margin ?? EdgeInsets.zero,
        child: Padding(
          padding: EdgeInsets.all(padding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min, // Ajustar al contenido
            children: [
              if (title != null) ...[
                Text(
                  title!,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 16),
                const Divider(height: 1), // Línea separadora tenue
                const SizedBox(height: 16),
              ],
              child,
            ],
          ),
        ),
      ),
    );
  }
}
