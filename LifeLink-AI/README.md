# 🚑 LifeLink AI

> **Every patient. Everywhere. Instantly.** — The Intelligent Emergency Response Network.

Prototipo local (MVP) de la plataforma **LifeLink AI**: una capa de inteligencia que
**orquesta automáticamente** la respuesta ante una emergencia médica, desde el primer
segundo del evento hasta el ingreso al prestador de salud óptimo.

Construido con **Django + SQLite + Leaflet**, corre 100 % local y sin claves de API.

---

## Los 3 pilares

| Pilar | Qué hace | Dónde está |
|-------|----------|-----------|
| 🟢 **Preparar** | Perfil "Always Ready" del paciente (condiciones, alergias, medicación, contactos, cobertura) + planes de viaje preventivos. | `Paciente`, `Planes de viaje` |
| 🟡 **Detectar** | Activación por botón SOS, caída (wearable), choque vehicular, biométrico o voz. | Panel **SOS** del Dashboard |
| 🔴 **Orquestar** | El **Emergency Orchestrator**: triage, scoring de prestadores y journey automático en segundos. | `core/orchestrator.py` |

---

## El corazón: el Emergency Orchestrator

Ante un evento (paciente + tipo + ubicación GPS) el motor:

1. **Triage** (`core/triage.py`): determina urgencia (escala tipo ESI 1–5) y la especialidad
   requerida, ajustando por antecedentes del paciente.
2. **Scoring transparente** (`core/orchestrator.py`): puntúa cada prestador con una rúbrica
   ponderada y **explicable** (se ve el desglose en la UI):

   | Dimensión | Peso | Criterio |
   |-----------|-----:|----------|
   | Cercanía | 34 | distancia de ruta → ETA de ambulancia |
   | Especialidad | 22 | ¿tiene la especialidad que el evento requiere? |
   | Cobertura | 18 | ¿el prestador acepta la obra social del paciente? |
   | Calidad clínica | 12 | rating 0–5 |
   | Disponibilidad | 9 | guardia abierta + camas libres |
   | Trauma | 5 | nivel de centro de trauma (si aplica) |
   | Idioma | +3 | bonus situacional (relevante en el exterior) |

3. **Journey automático**: genera el timeline de acciones (geolocalización ✓, triage ✓,
   cobertura ✓, prestador ✓, ambulancia 🚑, historia clínica 📋, familia 👨‍👩‍👧,
   aseguradora 📞, traducción 🌐, monitoreo 📡).

Es **determinístico y local** — modela exactamente cómo decidiría la capa de IA en producción,
pero sin depender de servicios externos.

---

## Setup

```powershell
# 1. Entorno + dependencias
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Base de datos + datos demo
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo

# 3. Server
.\.venv\Scripts\python.exe manage.py runserver
```

Abrí **http://127.0.0.1:8000/**

> Admin opcional: `python manage.py createsuperuser` → http://127.0.0.1:8000/admin/

---

## Cómo probarlo (demo flow)

1. **Dashboard** → panel **Simular emergencia**: elegí tipo (ej. *Paro cardíaco*), la
   detección (*botón SOS*) y la ubicación (chips `🏠 En casa`, `🏙️ Microcentro`,
   `🛣️ Autopista`, `✈️ Miami`, o click en el mapa).
2. **🚨 Activar SOS** → el orquestador elige el prestador óptimo y abrís el **Emergency Journey**.
3. Mirá el **timeline** de acciones automáticas y la sección **"Por qué este prestador"**
   con el desglose del puntaje contra los demás candidatos.
4. Probá el escenario **✈️ Miami** para ver la **traducción médica** activarse en el exterior.
5. **Planes de viaje** → generá un Emergency Readiness Plan para *Madrid*, *São Paulo*, etc.

---

## Estructura

```
LifeLink-AI/
├─ manage.py
├─ requirements.txt
├─ lifelink/            # configuración del proyecto
│  ├─ settings.py
│  └─ urls.py
└─ core/                # app principal
   ├─ models.py         # paciente, prestadores, emergencias, viajes
   ├─ triage.py         # reglas de urgencia por tipo de evento
   ├─ geo.py            # distancia haversine + ETA
   ├─ orchestrator.py   # 🧠 motor de decisión + timeline
   ├─ travel.py         # generador de Smart Travel Plans
   ├─ views.py / urls.py
   ├─ admin.py          # edición completa de datos
   ├─ templates/core/   # UI estilo Apple + mapas Leaflet
   └─ management/commands/seed_demo.py
```

---

## Roadmap (del business plan)

- [x] **Fase 1 (MVP)** — orquestación con geolocalización, triage y scoring explicable + viajero internacional.
- [ ] **Fase 2** — integración real con aseguradoras, hospitales y ambulancias (APIs).
- [ ] **Fase 3** — wearables / sensores biométricos para activación automática real.
- [ ] **Fase 4** — plataforma abierta (aerolíneas, hoteles, gobiernos) vía API.
- [ ] **Fase 5** — capacidades predictivas (detectar el evento antes de que ocurra).

---

## Notas

- **Datos clínicos = ficticios**, solo para demo. Editá el paciente en el admin con datos reales.
- **Seguridad**: prototipo local (`DEBUG=True`, sin auth). Antes de exponerlo a una red:
  `DEBUG=False`, restringir `ALLOWED_HOSTS`, rotar `SECRET_KEY` y agregar autenticación.
- Re-correr `seed_demo` **borra** pacientes/prestadores/eventos/planes y los recrea.
