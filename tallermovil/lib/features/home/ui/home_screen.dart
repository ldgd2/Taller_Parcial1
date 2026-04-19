import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FieldWork Central'),
        actions: [
          IconButton(icon: const Icon(Icons.notifications_outlined), onPressed: () {}),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('¡Hola de nuevo!', style: AppTextStyles.h1),
            const SizedBox(height: 8),
            Text('Este es el resumen de tu cuenta y vehículos.', style: AppTextStyles.bodyMedium),
            const SizedBox(height: 32),
            
            // Banner rápido
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.primaryMuted.withAlpha(100),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.primary),
              ),
              child: Row(
                children: [
                  const Icon(Icons.shield_outlined, color: AppColors.primary, size: 40),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Protección Activa', style: AppTextStyles.h3),
                        Text('Vehículos listos para asistencia S.O.S', style: AppTextStyles.bodyMedium),
                      ],
                    ),
                  )
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            Text('Emergencias Recientes', style: AppTextStyles.h2),
            const SizedBox(height: 16),
            
            GlassCard(
              onTap: () {},
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Audi Q5 (ABC-123)', style: AppTextStyles.h3),
                      const StatusBadge(text: 'En Taller', status: BadgeStatus.info),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Fallo térmico reportado el 15/Oct. Asignado a Taller Los Pinos.', style: AppTextStyles.bodyMedium),
                ],
              ),
            ),
            
            // Espacio al final para que no tape el FAB
            const SizedBox(height: 100),
          ],
        ),
      ),
    );
  }
}
