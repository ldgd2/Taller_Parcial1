import 'package:flutter/material.dart';
import '../../../shared/components/cards/t_card.dart';
import '../../../shared/components/feedback/t_badge.dart';
import '../../../shared/components/layout/t_spacing.dart';
import '../../../shared/components/typography/t_text.dart';
import '../../../shared/components/loaders/t_loader.dart';
import 'home_controller.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final HomeController controller;

  @override
  void initState() {
    super.initState();
    controller = HomeController();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AnimatedBuilder(
        animation: controller,
        builder: (context, child) {
          if (controller.isLoading) {
            return const Center(child: TLoader());
          }

          return RefreshIndicator(
            onRefresh: controller.loadData,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TText.h1('¡Hola de nuevo!'),
                  TSpacing.verticalSmall(),
                  TText.body('Este es el resumen de tu cuenta y vehículos.'),
                  TSpacing.verticalLarge(),
                  
                  TText.h2('Mis Vehículos'),
                  TSpacing.verticalMedium(),
                  
                  if (controller.vehicles.isEmpty)
                    TCard(
                      child: Center(
                        child: TText.body('No tienes vehículos registrados.'),
                      ),
                    )
                  else
                    ...controller.vehicles.map((v) => Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: TCard(
                        onTap: () {},
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                TText.h3('${v['marca']} ${v['modelo']}'),
                                TBadge.success(v['placa']),
                              ],
                            ),
                            TSpacing.verticalSmall(),
                            TText.body('Año: ${v['anio']}'),
                          ],
                        ),
                      ),
                    )),
                  
                  TSpacing.verticalLarge(),
                  TText.h2('Emergencias Recientes'),
                  TSpacing.verticalMedium(),
                  
                  TCard(
                    child: TText.body('No hay emergencias recientes.'),
                  ),
                  
                  TSpacing(height: 100),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
