# 🚀 Guía de Desarrollo - Taller Móvil (Flutter)

Esta guía explica la arquitectura del proyecto, cómo crear nuevos módulos y cómo utilizar el sistema de componentes premium (**T-System**).

---

## 1. Arquitectura del Proyecto

El proyecto sigue una estructura modular basada en **Features**. Cada funcionalidad importante tiene su propia carpeta.

```text
lib/
├── core/               # Configuraciones globales (Tema, Red, Storage)
├── shared/             # Componentes reutilizables (T-System)
└── features/           # Módulos de la aplicación
    └── [nombre_modulo]/
        ├── data/       # Servicios y APIs
        ├── models/     # Modelos de datos
        └── views/      # Interfaces de usuario y Controladores
```

---

## 2. Cómo crear un nuevo módulo (Ejemplo: `perfil`)

### Paso A: Definir el Modelo (`models/perfil.dart`)
Crea una clase que represente tus datos.
```dart
class Perfil {
  final String nombre;
  final String email;

  Perfil({required this.nombre, required this.email});

  factory Perfil.fromJson(Map<String, dynamic> json) => Perfil(
    nombre: json['nombre'],
    email: json['email'],
  );
}
```

### Paso B: Crear el Servicio (`data/perfil_service.dart`)
Define las llamadas al backend.
```dart
class PerfilService {
  final ApiClient apiClient;
  PerfilService(this.apiClient);

  Future<Perfil> getInfo() async {
    final response = await apiClient.dio.get('/usuarios/perfil');
    return Perfil.fromJson(response.data);
  }
}
```

### Paso C: Crear el Controlador (`views/perfil_controller.dart`)
Gestiona el estado de la vista usando `ChangeNotifier`.
```dart
class PerfilController extends ChangeNotifier {
  bool isLoading = false;
  Perfil? data;

  Future<void> load() async {
    isLoading = true;
    notifyListeners();
    // ... lógica de carga ...
    isLoading = false;
    notifyListeners();
  }
}
```

### Paso D: La Vista (`views/perfil_view.dart`)
Usa `AnimatedBuilder` para reaccionar a los cambios del controlador.

---

## 3. Uso del T-System (Componentes Premium)

Hemos creado una capa de componentes propia para asegurar un diseño consistente y elegante. **No uses widgets básicos de Flutter si existe un componente T-System.**

### 🅰️ Tipografía (`TText`)
Soporta temas automáticos y truncado de texto.
```dart
TText.h1('Título Gigante')
TText.h3('Subtítulo')
TText.body('Texto normal del sistema')
TText.label('Texto pequeño o etiquetas', color: AppColors.primary)
```

### 🅱️ Espaciado (`TSpacing`)
Evita usar `SizedBox` con números mágicos.
```dart
TSpacing.verticalSmall()    // 8px
TSpacing.verticalMedium()   // 16px
TSpacing.horizontalLarge()  // 24px
```

### 🅾️ Botones (`TButton`)
Botones con estados de carga y variantes.
```dart
TButton(
  label: 'Enviar Reporte',
  onPressed: () => print('Click!'),
  icon: Icons.send,
  variant: TButtonVariant.primary, // O .outline, .danger
  isLoading: controller.isUploading,
)
```

### 💎 Tarjetas (`TCard`)
Efecto de cristal y sombras suaves.
```dart
TCard(
  onTap: () => print('Ir al detalle'),
  child: Column(
    children: [
      TText.h3('Mi Tarjeta'),
      TSpacing.verticalSmall(),
      TText.body('Contenido de la tarjeta'),
    ],
  ),
)
```

### 🏷️ Badges (`TBadge`)
Para estados (Pendiente, Éxito, etc.)
```dart
TBadge.success('Completado')
TBadge.warning('Pendiente')
TBadge.error('Cancelado')
```

---

## 4. Mejores Prácticas

1.  **Manejo de Errores**: Usa `TSnackbar.error(context, message)` para mostrar errores al usuario de forma elegante.
2.  **Carga de Datos**: Siempre muestra un `TLoader()` mientras `controller.isLoading` sea verdadero.
3.  **Ubicación**: Usa `LocationService.getCurrentLocation()` para GPS y `LocationService.getAddressFromLatLng()` para la dirección escrita.
4.  **Multimedia**: Las URLs del backend suelen ser relativas. Usa `_fixUrl(url)` en tus vistas para añadir el host del servidor.

---

## 5. Ejemplo de una Vista Completa

```dart
class MiNuevaVista extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            TText.h1('Bienvenido'),
            TSpacing.verticalLarge(),
            TCard(
              child: TText.body('Este es un ejemplo de implementación rápida.'),
            ),
            TSpacing.verticalMedium(),
            TButton(label: 'Aceptar', onPressed: () {}),
          ],
        ),
      ),
    );
  }
}
```
