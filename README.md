# 🇲🇽 Mexico Toy Sales: Análisis de Negocio y Segmentación

Proyecto integral de análisis de datos, ingeniería y business intelligence enfocado en el rendimiento comercial de la cadena **Maven Toys** en México. Este repositorio documenta el flujo de trabajo completo, desde la gestión de bases de datos relacionales y scripts en Python hasta la segmentación de tiendas y la visualización ejecutiva en Power BI.

---

## 🛠️ Estructura del Repositorio

```text
mexico_toy_sales/
│
├── data/                    # Archivos de datos originales (CSV) y base de datos SQLite
│   ├── raw/                 # Datos fuente (sales, products, stores, inventory, calendar)
│   └── mexico_toy_sales.db  # Base de datos SQLite principal
│
├── src/                     # Scripts de Python para procesamiento y análisis
│   ├── carga.py             # Automatización de carga de datos a SQLite
│   └── segmentacion_tiendas.py # Análisis avanzado de tiendas y productos críticos
│
├── sql/                     # Consultas SQL estructuradas para el negocio
│   └── consultas_negocio.sql # CTEs para segmentación y métricas clave
│
├── dashboard/               # Recursos y archivos del reporte interactivo (Power BI)
├── notebooks/               # Cuadernos Jupyter para EDA (Exploratory Data Analysis)
└── README.md                # Documentación oficial del proyecto

---

## 📊 Hallazgos y Objetivos Clave

Segmentación de Tiendas:

Se estableció un promedio general de ingresos por tienda de $288,891.45.

Se identificaron sucursales con rendimiento crítico por debajo del umbral (destacando casos como Campeche 2, La Paz 1 y Cuernavaca 1) para enfocar estrategias comerciales y operativas específicas.

Análisis de Productos Críticos (Bottom 10):

Evaluación de artículos con menor rotación e ingresos (ej. Uno Card Game, Classic Dominoes, Playfoam) para optimizar la gestión de inventarios y campañas de marketing.

Modelo de Datos (Star Schema):

Relaciones estructuradas entre la tabla de hechos de ventas (sales) y las dimensiones de productos, tiendas y calendario para garantizar cálculos precisos.

---

## ⚙️ Requisitos Técnicos y Entorno
El proyecto utiliza Python y bibliotecas especializadas para análisis de datos y conectividad con bases de datos relacionales.

Python 3.x

Pandas (Manipulación y análisis de estructuras de datos)

SQLite3 (Gestión de base de datos embebida)

Instalación del Entorno Virtual
1. Clona el repositorio y activa tu entorno virtual:

Bash
python -m venv .venv
source .venv/Scripts/activate  # En Windows (Git Bash / PowerShell)

2.Ejecuta el script de segmentación y análisis directamente:

Bash
python src/segmentacion_tiendas.py

---

## 📈 Dashboard Interactivo (Power BI)
El modelo de datos y las métricas calculadas se integran en un reporte interactivo estructurado en tres niveles:

Resumen Ejecutivo: KPIs globales de ingresos, unidades y evolución temporal.

Segmentación de Tiendas: Vista comparativa frente a la línea base de rendimiento y filtros por tipo de ubicación (Downtown, Commercial, Residential).

Productos Críticos: Identificación del Bottom 10 de artículos para la toma de decisiones de inventario.

---

## 🚀 Control de Versiones
El desarrollo del proyecto se administra mediante flujos de ramas en Git:

main: Rama de producción y entregas estables.

developer: Rama activa para integración de scripts de Python, consultas SQL y validaciones de datos.
