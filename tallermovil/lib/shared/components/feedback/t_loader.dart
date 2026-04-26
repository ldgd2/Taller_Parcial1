import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';

class TLoader extends StatelessWidget {
  final double size;
  final Color? color;
  final String? message;

  const TLoader({
    super.key,
    this.size = 40.0,
    this.color,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    final loader = Center(
      child: SizedBox(
        width: size,
        height: size,
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(color ?? AppColors.primary),
          strokeWidth: 3,
        ),
      ),
    );

    if (message != null) {
      return Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          loader,
          const SizedBox(height: 16),
          Text(
            message!,
            style: TextStyle(color: color ?? AppColors.textPrimary),
          ),
        ],
      );
    }

    return loader;
  }

  static void show(BuildContext context, {String? message}) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => PopScope(
        canPop: false,
        child: TLoader(message: message),
      ),
    );
  }

  static void hide(BuildContext context) {
    Navigator.of(context).pop();
  }
}
