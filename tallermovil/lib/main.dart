import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import 'core/theme/app_theme.dart';
import 'core/theme/app_colors.dart';
import 'shared/widgets/primary_button.dart';
import 'shared/widgets/custom_text_field.dart';
import 'shared/widgets/glass_card.dart';
import 'shared/widgets/status_badge.dart';

import 'features/home/ui/main_navigation_screen.dart';

void main() {
  runApp(const TallerMovilApp());
}

class TallerMovilApp extends StatelessWidget {
  const TallerMovilApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Taller Móvil OS',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme, // Inyectando nuestro Design System
      home: const MainNavigationScreen(),
    );
  }
}

class ThemeShowcaseScreen extends StatefulWidget {
  const ThemeShowcaseScreen({super.key});

  @override
  State<ThemeShowcaseScreen> createState() => _ThemeShowcaseScreenState();
}

class _ThemeShowcaseScreenState extends State<ThemeShowcaseScreen> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FieldWork OS Components'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Typografía
            Text('Typography', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            Text('Header 1', style: Theme.of(context).textTheme.displayLarge),
            Text('Header 2', style: Theme.of(context).textTheme.displayMedium),
            Text('Header 3', style: Theme.of(context).textTheme.displaySmall),
            const SizedBox(height: 8),
            Text('This is a body text displaying the Inter font mapping exactly like the web. Dynamic, legible, and crisp.', style: Theme.of(context).textTheme.bodyMedium),
            
            const SizedBox(height: 32),
            
            // Badges
            Text('Status Badges', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                StatusBadge(text: 'En Curso', status: BadgeStatus.info),
                StatusBadge(text: 'Completado', status: BadgeStatus.success),
                StatusBadge(text: 'Critico', status: BadgeStatus.error),
                StatusBadge(text: 'Pendiente', status: BadgeStatus.warning),
              ],
            ).animate().fadeIn().slideX(),

            const SizedBox(height: 32),

            // Inputs
            Text('Form Controls', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            const CustomTextField(
              label: 'Patente / Placa',
              hint: 'Ej: AB 123 CD',
              prefixIcon: Icon(Icons.directions_car_outlined, color: AppColors.textMuted),
            ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1),

            const SizedBox(height: 32),

            // Tarjetas (GlassCards)
            Text('Surface Cards (Glass)', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            GlassCard(
              onTap: () {},
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Audi Q5 - Fallo Motor', style: Theme.of(context).textTheme.displaySmall),
                      const StatusBadge(text: 'Urgente', status: BadgeStatus.error),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Operador reportó humo saliendo por la parte frontal después de impacto leve.', style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ).animate().fadeIn(delay: 400.ms).scale(begin: const Offset(0.95, 0.95)),

            const SizedBox(height: 32),

            // Botones
            Text('Buttons & Actions', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            PrimaryButton(
              text: 'Asignar Técnico',
              icon: Icons.person_add_outlined,
              isLoading: _isLoading,
              onPressed: () async {
                setState(() => _isLoading = true);
                await Future.delayed(2.seconds);
                setState(() => _isLoading = false);
              },
            ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.1),
            
            const SizedBox(height: 16),
            
            PrimaryButton(
              text: 'Rechazar Solicitud',
              icon: Icons.close,
              isDestructive: true,
              onPressed: () {},
            ).animate().fadeIn(delay: 700.ms).slideY(begin: 0.1),
          ],
        ),
      ),
    );
  }
}
