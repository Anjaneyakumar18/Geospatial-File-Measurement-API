# Geospatial File Measurement API

A Django-based geospatial file processing application that accepts **KML files** and **ZIP archives containing Shapefiles**, extracts their geographic features, handles coordinate reference systems (CRS), and calculates measurements such as **polygon area** and **line length**.

The project provides both:

- A simple web interface for uploading and viewing results.
- REST API endpoints for programmatic access.

---

## Features

- Upload `.kml` files.
- Upload `.zip` files containing Shapefiles.
- Generate a unique UUID for every uploaded file.
- Extract geospatial feature information.
- Identify geometry types such as:
  - Point
  - LineString
  - Polygon
  - MultiPoint
  - MultiLineString
  - MultiPolygon
- Display feature properties.
- Detect the original CRS.
- Reproject geographic CRS to a suitable projected CRS before measurements.
- Calculate:
  - Polygon → Area
  - LineString → Length
  - Point → No measurement required
- Gracefully handle unsupported geometries.
- Store uploaded file metadata in a Django database.
- Provide REST API endpoints.
- Provide HTML pages for file details and measurements.

---

# 1. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Django | Web framework |
| Django REST Framework | REST API |
| GeoPandas | Geospatial file processing |
| Shapely | Geometry operations |
| PyProj | CRS and coordinate transformations |
| Fiona | Geospatial file I/O |
| Pandas | Data processing and missing-value handling |
| SQLite | Development database |
| HTML/CSS/JavaScript | Frontend |
| Git/GitHub | Version control |

---

# 2. Project Structure

```text
Geospatial/
│
├── manage.py
│
├── Geospatial/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── Geoapp/
│   │
│   ├── migrations/
│   │
│   ├── templates/
│   │   └── Geoapp/
│   │       ├── home.html
│   │       ├── result.html
│   │       ├── file_details.html
│   │       └── measurements.html
│   │
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── media/
│
├── .gitignore
├── requirements.txt
└── README.md
```

### Important files

### `models.py`

Defines the database model used to store uploaded files and their processing information.

### `services.py`

Contains the main geospatial processing logic:

- Reading KML/Shapefile data.
- CRS detection.
- CRS transformation.
- Feature extraction.
- Area calculation.
- Length calculation.
- Property cleaning.

### `views.py`

Contains:

- HTML views.
- REST API endpoints.

### `urls.py`

Defines the application's HTML routes and REST API routes.

---

# 3. How to Run Locally

## Prerequisites

Install:

- Python 3.10+
- Git

Python 3.13 was used during development.

Check your Python version:

```bash
python --version
```

or on Windows:

```bash
py --version
```

---

## Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project:

```bash
cd Geospatial
```

---

## Step 2: Create a virtual environment

Windows:

```bash
py -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(venv) E:\Djnago\Geospatial>
```

---

## Step 3: Install dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

---

## Step 4: Apply database migrations

Run:

```bash
py manage.py makemigrations
```

Then:

```bash
py manage.py migrate
```

This creates the SQLite database and required Django tables.

---

## Step 5: Start the development server

```bash
py manage.py runserver
```

You should see:

```text
Starting development server at http://127.0.0.1:8000/
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 4. How the Application Works

The application has two main parts:

1. Web interface
2. REST API

The overall flow is:

```text
User
 │
 │ Upload KML / ZIP
 ▼
Home Page
 │
 ▼
POST /api/files/
 │
 ▼
Django receives file
 │
 ▼
GeoPandas reads file
 │
 ▼
Detect CRS
 │
 ├── Geographic CRS
 │       │
 │       ▼
 │   Reproject to suitable
 │   projected CRS
 │
 └── Projected CRS
         │
         ▼
   Use existing CRS
 │
 ▼
Extract Features
 │
 ├── Point
 │
 ├── LineString
 │
 └── Polygon
 │
 ▼
Calculate Measurements
 │
 ├── Point → None
 ├── LineString → Length
 └── Polygon → Area
 │
 ▼
Save file metadata
 │
 ▼
Generate UUID
 │
 ▼
Return response
```

---

# 5. File Upload Flow

When a user selects a KML or ZIP file and clicks **Upload & Process**, the frontend sends a multipart request to:

```text
POST /api/files/
```

The backend:

1. Validates the uploaded file.
2. Accepts `.kml` and `.zip`.
3. Creates a `GeoFile` database record.
4. Generates a UUID for the file.
5. Reads the file using GeoPandas.
6. Processes the geospatial features.
7. Detects the CRS.
8. Calculates measurements.
9. Updates the database record.
10. Returns the generated UUID and endpoint URLs.

Example response:

```json
{
    "id": "8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345",
    "filename": "sample.kml",
    "status": "COMPLETED",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "measurement_crs": "EPSG:32644",
    "detail_url": "/api/files/8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345/",
    "measurements_url": "/api/files/8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345/measurements/",
    "result_url": "/result/8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345/"
}
```

---

# 6. CRS Handling

Area and length should not be calculated directly when the geometry is stored in a geographic CRS such as:

```text
EPSG:4326
```

EPSG:4326 represents coordinates using latitude and longitude in degrees.

Calculating:

```python
geometry.area
```

or:

```python
geometry.length
```

directly on geographic coordinates would produce values based on degrees rather than meaningful physical units.

Therefore, the application checks the CRS.

### Geographic CRS

If the input CRS is geographic:

```python
gdf.crs.is_geographic
```

the application estimates a suitable UTM CRS:

```python
measurement_crs = gdf.estimate_utm_crs()
```

The GeoDataFrame is then reprojected:

```python
measurement_gdf = gdf.to_crs(measurement_crs)
```

Measurements are calculated on the projected geometry.

### Projected CRS

If the input data is already in a projected CRS, the existing CRS is used.

---

# 7. Measurement Logic

## Point

Points do not have an area or length measurement.

```text
Point
  ↓
No measurement required
```

---

## LineString

For a LineString:

```python
projected_geometry.length
```

is used.

The result is returned in:

```text
meters
```

Example:

```text
Length: 125.43 m
```

---

## Polygon

For a Polygon:

```python
projected_geometry.area
```

is used.

The result is returned in:

```text
square meters (m²)
```

Example:

```text
Area: 15432.28 m²
```

---

# 8. Supported Geometry Types

| Geometry | Measurement |
|---|---|
| Point | None |
| MultiPoint | None |
| LineString | Length |
| MultiLineString | Length |
| Polygon | Area |
| MultiPolygon | Area |
| Other | Not supported |

Unsupported geometries are handled gracefully rather than causing the entire request to fail.

---

# 9. Feature Information

For every feature, the application extracts:

```text
Feature ID
Geometry Type
Geometry
CRS
Properties
Measurement Type
Measurement
Unit
Status
```

Example:

```json
{
    "feature_id": 1,
    "geometry_type": "Polygon",
    "geometry": "POLYGON ((...))",
    "crs": "EPSG:4326",
    "measurement_type": "Area",
    "measurement": 15432.28,
    "unit": "m²",
    "status": "SUCCESS"
}
```

---

# 10. REST API

The application exposes three required API endpoints.

---

## 10.1 Upload File

### Endpoint

```http
POST /api/files/
```

### Content Type

```text
multipart/form-data
```

### Form field

```text
file
```

### Example using cURL

```bash
curl -X POST http://127.0.0.1:8000/api/files/ \
     -F "file=@sample.kml"
```

### Response

```json
{
    "id": "8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345",
    "filename": "sample.kml",
    "status": "COMPLETED",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "measurement_crs": "EPSG:32644"
}
```

---

# 11. Get File Details

### Endpoint

```http
GET /api/files/{id}/
```

Example:

```text
GET /api/files/8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345/
```

Example response:

```json
{
    "id": "8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345",
    "filename": "sample.kml",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "measurement_crs": "EPSG:32644",
    "status": "COMPLETED",
    "error": null
}
```

---

# 12. Get Measurements

### Endpoint

```http
GET /api/files/{id}/measurements/
```

Example:

```text
GET /api/files/8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345/measurements/
```

The response contains the processed features and their measurements.

Example:

```json
{
    "id": "8f3c2e51-6b8a-4a9d-bf21-91c8e7d12345",
    "filename": "sample.kml",
    "feature_count": 3,
    "crs": "EPSG:4326",
    "measurement_crs": "EPSG:32644",
    "features": [
        {
            "feature_id": 0,
            "geometry_type": "Point",
            "measurement": null,
            "unit": null,
            "status": "NO_MEASUREMENT_REQUIRED"
        },
        {
            "feature_id": 1,
            "geometry_type": "LineString",
            "measurement": 125.43,
            "unit": "m",
            "status": "SUCCESS"
        },
        {
            "feature_id": 2,
            "geometry_type": "Polygon",
            "measurement": 15432.28,
            "unit": "m²",
            "status": "SUCCESS"
        }
    ]
}
```

---

# 13. Web Interface

The application also provides HTML pages.

### Home

```text
/
```

Used to upload KML or ZIP files.

After a successful upload, the generated file UUID is displayed.

The page provides links to:

- File Details
- Measurements
- Complete Results

### File Details

```text
/file-details/{id}/
```

Displays:

- File ID
- Filename
- Status
- Feature count
- Original CRS
- Measurement CRS
- Creation time
- Error information if applicable

### Measurements

```text
/measurements/{id}/
```

Displays the calculated measurements and feature information.

### Complete Results

```text
/result/{id}/
```

Displays the complete processed geospatial result.

---

# 14. Database Model

The application uses a `GeoFile` model.

Important fields:

```text
id
file
filename
feature_count
crs
measurement_crs
status
error_message
created_at
```

The `id` field is a UUID:

```python
id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
)
```

This UUID uniquely identifies an uploaded file and is used by the API endpoints.

---

# 15. Python Packages

The main packages used by the project are:

### Django

Used for:

- Web application
- URL routing
- Templates
- Database models
- File uploads

```text
Django
```

### Django REST Framework

Used to implement the REST API endpoints.

```text
djangorestframework
```

### GeoPandas

Used to read and process geospatial datasets.

```text
geopandas
```

### Shapely

Used for geometry representation and geometry operations.

```text
shapely
```

### PyProj

Used for coordinate reference systems and CRS transformations.

```text
pyproj
```

### Fiona

Used by the geospatial stack for reading/writing supported geospatial file formats.

```text
fiona
```

### Pandas

Used for handling tabular feature properties and missing values such as `NaN` and `NaT`.

```text
pandas
```

---

# 16. Install Packages Manually

If `requirements.txt` is not available, the main dependencies can be installed using:

```bash
pip install django
pip install djangorestframework
pip install geopandas
pip install pandas
pip install shapely
pip install pyproj
pip install fiona
```

Or simply:

```bash
pip install -r requirements.txt
```

---

# 17. Error Handling

The application handles several error conditions:

### No file uploaded

Returns:

```text
Please upload a file.
```

### Unsupported file type

Only:

```text
.kml
.zip
```

are accepted.

### Empty geospatial file

The application returns:

```text
The uploaded file contains no features.
```

### Missing CRS

If the file has no CRS, the application does not assume a CRS automatically.

### Unable to determine measurement CRS

If a suitable projected CRS cannot be determined, processing fails with an appropriate error.

### Unsupported geometry

Unsupported geometries receive:

```text
status = NOT_SUPPORTED
```

instead of crashing the entire processing operation.

---

# 18. Development Notes

This project uses SQLite for local development.

Uploaded files are stored under:

```text
media/geospatial/
```

The `media/` directory should not be committed to Git because it contains uploaded files.

The SQLite database is also intended for local development and should not normally be committed.

---

# 19. Running the Project — Quick Version

After cloning the repository:

```bash
cd Geospatial
```

Create environment:

```bash
py -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Migrate:

```bash
py manage.py migrate
```

Run:

```bash
py manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 20. Example User Flow

```text
1. Open application
       ↓
2. Select sample.kml
       ↓
3. Click Upload & Process
       ↓
4. Django receives the file
       ↓
5. GeoPandas reads the file
       ↓
6. CRS is detected
       ↓
7. Geographic CRS is reprojected if necessary
       ↓
8. Features are processed
       ↓
9. Area / length is calculated
       ↓
10. File metadata is stored
       ↓
11. UUID is generated
       ↓
12. UUID is shown to the user
       ↓
13. User can view:
       ├── File Details
       ├── Measurements
       └── Complete Results
```

---

# 21. Future Improvements

Possible improvements include:

- Add authentication and authorization.
- Store geospatial data using PostGIS.
- Support additional geospatial formats.
- Add asynchronous processing for large files.
- Add file-size validation.
- Add better ZIP/Shapefile validation.
- Add spatial visualization on an interactive map.
- Cache processed measurements instead of recalculating them.
- Add automated tests.
- Add Docker support.
- Deploy using PostgreSQL/PostGIS instead of SQLite.

---

# 22. License

This project was created as a geospatial backend/API implementation project.
```

**One thing before you push it:** after saving this as `README.md`, run:

```bash
git add README.md
git commit -m "Add project documentation"
git push origin main
```

That gives the evaluator a clear path from **clone → install → run → understand architecture → test the 3 APIs**.
