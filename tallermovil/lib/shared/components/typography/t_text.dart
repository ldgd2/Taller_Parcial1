import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_text_styles.dart';

class TText extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;
  final Color? color;

  const TText(
    this.text, {
    super.key,
    this.style,
    this.textAlign,
    this.maxLines,
    this.overflow,
    this.color,
  });

  factory TText.h1(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.h1, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.h2(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.h2, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.h3(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.h3, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.h4(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.h4, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.body(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.bodyMedium, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.bodyLarge(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.bodyLarge, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.bodySmall(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.bodySmall, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.label(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.label, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  factory TText.caption(String text, {Key? key, TextAlign? textAlign, Color? color, int? maxLines, TextOverflow? overflow}) {
    return TText(text, key: key, style: AppTextStyles.overline, textAlign: textAlign, color: color, maxLines: maxLines, overflow: overflow);
  }

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: color != null ? style?.copyWith(color: color) : style,
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }
}
