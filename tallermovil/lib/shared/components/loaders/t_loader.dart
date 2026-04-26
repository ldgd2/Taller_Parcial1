import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';

class TLoader extends StatelessWidget {
  final double size;
  final Color? color;

  const TLoader({
    super.key, 
    this.size = 40.0,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CircularProgressIndicator(
        strokeWidth: 3,
        valueColor: AlwaysStoppedAnimation<Color>(color ?? AppColors.primary),
      ),
    );
  }
}
