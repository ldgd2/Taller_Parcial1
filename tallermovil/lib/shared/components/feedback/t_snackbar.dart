import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';

class TSnackbar {
  static void show(
    BuildContext context, {
    required String message,
    bool isError = false,
    bool isSuccess = false,
  }) {
    Color bgColor = AppColors.neutral800;
    if (isError) bgColor = AppColors.danger;
    if (isSuccess) bgColor = AppColors.success;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          message,
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: bgColor,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  static void error(BuildContext context, String message) {
    show(context, message: message, isError: true);
  }

  static void success(BuildContext context, String message) {
    show(context, message: message, isSuccess: true);
  }

  static void info(BuildContext context, String message) {
    show(context, message: message);
  }
}
