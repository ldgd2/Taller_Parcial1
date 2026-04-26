import 'package:flutter/material.dart';

class TSpacing extends StatelessWidget {
  final double width;
  final double height;

  const TSpacing({super.key, this.width = 0, this.height = 0});

  // Vertical spacing
  factory TSpacing.verticalXSmall() => const TSpacing(height: 4.0);
  factory TSpacing.verticalSmall() => const TSpacing(height: 8.0);
  factory TSpacing.verticalMedium() => const TSpacing(height: 16.0);
  factory TSpacing.verticalLarge() => const TSpacing(height: 24.0);
  factory TSpacing.verticalXLarge() => const TSpacing(height: 32.0);

  // Horizontal spacing
  factory TSpacing.horizontalXSmall() => const TSpacing(width: 4.0);
  factory TSpacing.horizontalSmall() => const TSpacing(width: 8.0);
  factory TSpacing.horizontalMedium() => const TSpacing(width: 16.0);
  factory TSpacing.horizontalLarge() => const TSpacing(width: 24.0);
  factory TSpacing.horizontalXLarge() => const TSpacing(width: 32.0);

  @override
  Widget build(BuildContext context) {
    return SizedBox(width: width, height: height);
  }
}
