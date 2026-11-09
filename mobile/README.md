# CareBridge Mobile App

[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B.svg?style=flat&logo=Flutter&logoColor=white)](https://flutter.dev)
[![Dart](https://img.shields.io/badge/Dart-3.x-0175C2.svg?style=flat&logo=Dart&logoColor=white)](https://dart.dev)
[![Material 3](https://img.shields.io/badge/Material-3-7C4DFF.svg?style=flat)](https://m3.material.io)

The official cross-platform mobile client for the **CareBridge AI** healthcare coordination platform. Built with Flutter, it empowers patients and their designated family caregivers to track post-discharge care journeys, log daily medications, monitor diagnostic report availability, and stay connected with care teams on any device.

---

## 📱 Features

- **Multi-Role Authentication**: Seamless login for Patients and Family Caregivers with built-in demo credentials chips for instant testing.
- **Dynamic Server Environment Selector**: Switch between the live Render Cloud backend, local PC backend (`localhost:8000`), or the Android Emulator gateway (`10.0.2.2:8000`) directly from the login screen.
- **Journey Timeline & Daily Tasks**:
  - Interactive task checklist categorized by urgency (`High Priority`, `Medium`, `Routine`).
  - Filtering by status: *All*, *Today's Focus*, *Pending*, and *Completed*.
  - Task completion toggling with instant server synchronization.
- **Medication Adherence Tracker**:
  - Daily dosage schedule organized by time of day (Morning, Afternoon, Evening, Night).
  - Adherence streak calculator to encourage consistent medication habits.
  - Quick action buttons to record taken doses.
- **Diagnostic Reports Checklist**:
  - Track required post-discharge labs (e.g., Blood tests, ECG, Scans).
  - Live status chips: `Available`, `Pending`, `Delayed`.
- **Caregiver Collaboration**: View linked family caregivers, permissions, and emergency contacts.
- **Material 3 Design**: Clean medical teal & blue palette with rounded cards, accessible typography, pull-to-refresh, and robust error handling.

---

## 📁 Directory Structure

```text
mobile/
├── lib/
│   ├── core/
│   │   ├── api_client.dart       # Network client with token injection & error mapping
│   │   ├── app_theme.dart        # Material 3 colors, typography, component themes
│   │   └── constants.dart        # Default endpoints & demo credentials
│   ├── models/
│   │   ├── user.dart             # User & authentication models
│   │   ├── task.dart             # Journey task & milestone models
│   │   ├── medication.dart       # Prescribed medication & adherence models
│   │   └── report.dart           # Diagnostic report models
│   ├── screens/
│   │   ├── login_screen.dart     # Auth screen with server switcher chips
│   │   ├── journey_screen.dart   # Main care timeline & task manager
│   │   ├── medication_screen.dart# Medication adherence tracker
│   │   ├── reports_screen.dart   # Diagnostic reports checklist
│   │   └── profile_screen.dart   # Patient info & linked caregivers
│   └── main.dart                 # App initialization, routing & state wrapper
├── android/                      # Native Android configuration & Gradle builds
├── ios/                          # Native iOS workspace
├── web/                          # Flutter Web entry point & manifest
└── pubspec.yaml                  # Dependencies and assets definition
```

---

## 🚀 Getting Started

### Prerequisites
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (version 3.13 or newer)
- Android Studio or VS Code with Flutter & Dart extensions
- (For Android APK builds) Android SDK with Platform 34+ and Build-Tools

---

### Installation & Setup

1. **Navigate to the mobile directory**:
   ```powershell
   cd mobile
   ```

2. **Install Flutter packages**:
   ```powershell
   flutter pub get
   ```

3. **Check available devices**:
   ```powershell
   flutter devices
   ```

---

## 💻 Running the App

### 1. In Google Chrome (Web)
```powershell
flutter run -d chrome
```

### 2. On Windows Desktop
```powershell
flutter run -d windows
```

### 3. On Android Emulator or Connected Phone
```powershell
flutter run -d <device_name_or_id>
```

> [!TIP]
> **Connecting to Localhost from Android**:
> - If running on the **Android Emulator**, select the **Android Emulator (10.0.2.2)** chip on the login screen.
> - If running on a **Physical Phone connected via USB**, run `adb reverse tcp:8000 tcp:8000` in your terminal and select the **Localhost (8000)** chip.
> - Or select **Render Cloud** to connect to the live cloud backend with zero local setup.

---

## 📦 Building Android APKs

### Debug APK (Recommended for quick testing)
```powershell
flutter build apk --debug
```
The output file will be generated at:
```text
mobile/build/app/outputs/flutter-apk/app-debug.apk
```

### Release APK
```powershell
flutter build apk --release
```
The output file will be generated at:
```text
mobile/build/app/outputs/flutter-apk/app-release.apk
```

---

## 🧪 Running Tests

Execute the Flutter unit and widget tests:
```powershell
flutter test
```

---

## 🔑 Demo Login Credentials

You can tap the pre-filled chips on the login screen or enter manually:

- **Patient**: `demo@carebridge.ai` | `carebridge123`
- **Caregiver**: `priya.demo@carebridge.ai` | `carebridge123`
