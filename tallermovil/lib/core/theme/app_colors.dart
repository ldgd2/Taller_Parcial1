import 'package:flutter/material.dart';

/// Tokens de color extraídos de la versión web (Tailwind CSS zinc/emerald/dark mode)
class AppColors {
  // Fondos
  static const Color background = Color(0xFF09090B); // zinc-950
  static const Color surface = Color(0xFF18181B); // zinc-900
  static const Color surfaceLight = Color(0xFF27272A); // zinc-800
  
  // Textos y Contenidos
  static const Color textPrimary = Color(0xFFFAFAFA); // zinc-50
  static const Color textSecondary = Color(0xFFA1A1AA); // zinc-400
  static const Color textMuted = Color(0xFF71717A); // zinc-500
  
  // Acentos (Verde Esmeralda)
  static const Color primary = Color(0xFF10B981); // emerald-500
  static const Color primaryHover = Color(0xFF059669); // emerald-600
  static const Color primaryMuted = Color(0xFF064E3B); // emerald-900
  
  // Estados
  static const Color error = Color(0xFFEF4444); // red-500
  static const Color errorBg = Color(0xFF7F1D1D); // red-900 (dim)
  
  static const Color warning = Color(0xFFF59E0B); // amber-500
  static const Color warningBg = Color(0xFF78350F); // amber-900 (dim)
  
  static const Color success = Color(0xFF10B981); // emerald-500
  static const Color successBg = Color(0xFF064E3B); // emerald-900 (dim)

  static const Color info = Color(0xFF3B82F6); // blue-500
  static const Color infoBg = Color(0xFF1E3A8A); // blue-900 (dim)

  // Bordes y divisores
  static const Color border = Color(0xFF3F3F46); // zinc-700
  static const Color borderLight = Color(0xFF52525B); // zinc-600
}
