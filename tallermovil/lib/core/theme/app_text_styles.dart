import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

class AppTextStyles {
  // Configuración base de la fuente principal (Inter)
  static final TextStyle base = GoogleFonts.inter(
    color: AppColors.textPrimary,
  );

  // Configuración para familia monospace (Space Mono/Roboto Mono)
  static final TextStyle mono = GoogleFonts.spaceMono(
    color: AppColors.primary,
  );

  // Títulos
  static final TextStyle h1 = base.copyWith(
    fontSize: 28,
    fontWeight: FontWeight.bold,
    letterSpacing: -0.5,
  );

  static final TextStyle h2 = base.copyWith(
    fontSize: 24,
    fontWeight: FontWeight.w700,
    letterSpacing: -0.5,
  );

  static final TextStyle h3 = base.copyWith(
    fontSize: 20,
    fontWeight: FontWeight.w600,
  );

  // Cuerpos de texto
  static final TextStyle bodyLarge = base.copyWith(
    fontSize: 16,
    fontWeight: FontWeight.normal,
  );

  static final TextStyle bodyMedium = base.copyWith(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: AppColors.textSecondary,
  );

  static final TextStyle bodySmall = base.copyWith(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: AppColors.textMuted,
  );

  // Etiquetas, Botones y Badges
  static final TextStyle label = base.copyWith(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
  );

  static final TextStyle overline = base.copyWith(
    fontSize: 10,
    fontWeight: FontWeight.w700,
    letterSpacing: 1.0,
    color: AppColors.textMuted,
    // equivalente a uppercase en web se suele aplicar en el Text widget
  );
}
