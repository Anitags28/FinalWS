# Sistema Recomendador de Películas con Web Semántica

Este proyecto implementa un sistema recomendador de películas utilizando tecnologías de Web Semántica, incluyendo RDF, SPARQL y Apache Jena Fuseki.

## Características Principales

- Registro y gestión de películas con metadatos semánticos
- Sistema de recomendación basado en preferencias del usuario
- Generación de opiniones inteligentes sobre películas
- Interfaz web intuitiva y responsive
- Base de conocimiento RDF con consultas SPARQL
- Pruebas unitarias automatizadas

## Tecnologías Utilizadas

- **Backend**: Python 3.8+
- **Framework Web**: Flask 3.0.0
- **Base de Conocimiento**: RDF (rdflib 7.0.0)
- **Base de Datos Semántica**: Apache Jena Fuseki
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Testing**: unittest, pytest

## Requisitos Previos

1. Python 3.8 o superior
2. Apache Jena Fuseki Server
3. pip (gestor de paquetes de Python)

## Instalación

### 1. Instalar Apache Jena Fuseki

1. Descargar Apache Jena Fuseki desde: https://jena.apache.org/download/
2. Descomprimir el archivo descargado
3. Navegar hasta la carpeta descomprimida
4. Iniciar Fuseki:
   - En Windows: `fuseki-server.bat`
   - En Linux/Mac: `./fuseki-server`

El servidor Fuseki estará disponible en: http://localhost:3030

### 2. Configurar el Entorno Python

1. Clonar o descargar este repositorio
2. Abrir una terminal en la carpeta del proyecto
3. Crear un entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

### 3. Configurar el Archivo .env

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:
```
FUSEKI_ENDPOINT=http://localhost:3030/movies
FUSEKI_USER=admin
FUSEKI_PASSWORD=admin
```

## Iniciar el Sistema

1. Asegurarse de que Apache Jena Fuseki está en ejecución
2. Abrir una terminal en la carpeta del proyecto
3. Activar el entorno virtual si no está activado:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Iniciar la aplicación:
```bash
python app/app.py
```

La aplicación estará disponible en: http://localhost:5000

## Uso del Sistema

1. **Agregar Películas**:
   - Usar el formulario en la izquierda para agregar nuevas películas
   - Ingresar título, director, género y calificación

2. **Ver Películas**:
   - Clic en "Todas las Películas" para ver el catálogo completo
   - Las películas se ordenan por calificación

3. **Gestionar Favoritos**:
   - Clic en el botón de corazón para marcar/desmarcar favoritos
   - Los favoritos se usan para generar recomendaciones

4. **Ver Recomendaciones**:
   - Clic en "Recomendaciones" para ver sugerencias personalizadas
   - Las recomendaciones se basan en tus películas favoritas

## Solución de Problemas

### Error de Conexión con Fuseki
Si aparece un error de conexión:
1. Verificar que Fuseki está en ejecución
2. Comprobar que la URL en el archivo `.env` es correcta
3. Verificar que el dataset 'movies' existe en Fuseki

### Error al Agregar Películas
Si las películas no se agregan:
1. Verificar que todos los campos del formulario están completos
2. Comprobar que la calificación es un número entre 1 y 5
3. Revisar los logs de la aplicación para más detalles

### Problemas con las Recomendaciones
Si las recomendaciones no aparecen:
1. Asegurarse de haber marcado algunas películas como favoritas
2. Verificar que hay suficientes películas en el sistema
3. Comprobar los logs para posibles errores

## Estructura del Proyecto

```
proyecto/
├── app/
│   ├── app.py              # Aplicación principal Flask
│   ├── sparql_manager.py   # Gestión de consultas SPARQL
│   └── movie_agent.py      # Lógica de recomendaciones
├── templates/
│   └── index.html          # Interfaz de usuario
├── venv/                   # Entorno virtual
├── .env                    # Configuración
├── requirements.txt        # Dependencias
└── README.md              # Este archivo
```

## Dependencias Principales

Las dependencias están listadas en `requirements.txt`:
- Flask
- rdflib
- SPARQLWrapper
- python-dotenv
- requests

## Notas Adicionales

- El sistema usa el puerto 5000 por defecto
- Fuseki debe estar ejecutándose en el puerto 3030
- Se recomienda tener al menos 5-10 películas para que el sistema de recomendaciones funcione óptimamente
- Los datos se almacenan en el triplestore de Fuseki, por lo que persistirán entre reinicios de la aplicación

## Funcionalidades

### Gestión de Películas
- Agregar nuevas películas con título, director, género y calificación
- Visualizar detalles de películas
- Marcar películas como favoritas

### Sistema de Recomendación
- Análisis de preferencias basado en géneros y directores favoritos
- Recomendaciones personalizadas según historial del usuario
- Generación de opiniones semánticas

### API REST
- `/add_movie` (POST): Agregar nueva película
- `/get_recommendations` (GET): Obtener recomendaciones
- `/movie_details/<id>` (GET): Obtener detalles de película
- `/favorite_movie` (POST): Marcar película como favorita

## Pruebas

Ejecutar las pruebas unitarias:
```bash
python -m pytest app/test_movie_agent.py
```

## Contribuir

1. Fork del repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Tu Nombre - [@tutwitter](https://twitter.com/tutwitter) - email@example.com

URL del Proyecto: [https://github.com/tuusuario/movie-recommender](https://github.com/tuusuario/movie-recommender) 