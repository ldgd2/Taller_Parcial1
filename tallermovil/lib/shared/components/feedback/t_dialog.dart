import 'package:flutter/material.dart';
import 'package:tallermovil/shared/components/buttons/t_button.dart';
import 'package:tallermovil/shared/components/typography/t_text.dart';

class TDialog extends StatelessWidget {
  final String title;
  final String message;
  final String confirmLabel;
  final String? cancelLabel;
  final VoidCallback onConfirm;
  final VoidCallback? onCancel;
  final bool isDanger;

  const TDialog({
    super.key,
    required this.title,
    required this.message,
    required this.onConfirm,
    this.confirmLabel = 'Aceptar',
    this.cancelLabel,
    this.onCancel,
    this.isDanger = false,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: TText.h3(title),
      content: TText.body(message),
      actions: [
        if (cancelLabel != null)
          TButton(
            label: cancelLabel!,
            variant: TButtonVariant.text,
            isFullWidth: false,
            onPressed: () {
              Navigator.of(context).pop();
              onCancel?.call();
            },
          ),
        TButton(
          label: confirmLabel,
          variant: isDanger ? TButtonVariant.danger : TButtonVariant.primary,
          isFullWidth: false,
          onPressed: () {
            Navigator.of(context).pop();
            onConfirm();
          },
        ),
      ],
    );
  }

  static Future<void> show(
    BuildContext context, {
    required String title,
    required String message,
    required VoidCallback onConfirm,
    String confirmLabel = 'Aceptar',
    String? cancelLabel,
    VoidCallback? onCancel,
    bool isDanger = false,
  }) {
    return showDialog(
      context: context,
      builder: (context) => TDialog(
        title: title,
        message: message,
        onConfirm: onConfirm,
        confirmLabel: confirmLabel,
        cancelLabel: cancelLabel,
        onCancel: onCancel,
        isDanger: isDanger,
      ),
    );
  }
}
