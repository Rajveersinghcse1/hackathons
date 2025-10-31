# AI Rockfall Prediction System - Complete Architecture Flow Chart

## System Overview Flow Chart

```mermaid
graph TB
    subgraph "Data Sources"
        A1[LiDAR .las files]
        A2[Geophone CSV data]
        A3[Piezometer sensor data]
        A4[GB-InSAR measurements]
        A5[Extensometer readings]
        A6[Weather station data]
        A7[YOLO image analysis]
        A8[Rockfall incident logs]
    end

    subgraph "Analysis Engine (Jupyter Notebooks)"
        B1[LiDAR_Rockfall_Prediction.ipynb<br/>- 3D point cloud processing<br/>- Feature extraction (38+ features)<br/>- K-means clustering<br/>- Random Forest/Gradient Boosting]
        B2[Geophone_Rockfall_Prediction.ipynb<br/>- Seismic signal processing<br/>- FFT frequency analysis<br/>- Magnitude calculation<br/>- Pattern recognition]
        B3[Piezometer_Landslide_Prediction.ipynb<br/>- Pressure monitoring<br/>- Time series analysis<br/>- Risk classification<br/>- Multi-class assessment]
        B4[GB_InSAR_Rockfall_Prediction.ipynb<br/>- Interferometric analysis<br/>- Ground deformation tracking<br/>- Velocity analysis<br/>- Risk mapping]
        B5[Extensometer_Analysis.ipynb<br/>- Crack opening analysis<br/>- Strain rate calculation<br/>- Stability assessment<br/>- Alert generation]
        B6[Automatic_Weather_Station_Analysis.ipynb<br/>- Environmental monitoring<br/>- Correlation analysis<br/>- Risk factor integration<br/>- Weather-based adjustments]
        B7[NewImageanalysis.ipynb<br/>- YOLOv8 object detection<br/>- Computer vision processing<br/>- Damage detection<br/>- Visual risk assessment]
    end

    subgraph "FastAPI Backend"
        C1[Data Ingestion API<br/>- File upload endpoints<br/>- Data validation<br/>- Format conversion]
        C2[Analysis Orchestration<br/>- Notebook execution<br/>- Parallel processing<br/>- Status tracking]
        C3[Results Aggregation<br/>- Multi-sensor fusion<br/>- Risk score calculation<br/>- Alert generation]
        C4[Database Layer<br/>- PostgreSQL integration<br/>- Historical data storage<br/>- Query optimization]
        C5[Real-time APIs<br/>- WebSocket connections<br/>- Live data streaming<br/>- Push notifications]
    end

    subgraph "Frontend Dashboard"
        D1[Authentication System<br/>- Login/Registration<br/>- JWT tokens<br/>- Role-based access]
        D2[Main Dashboard<br/>- Overall metrics<br/>- Risk heatmaps<br/>- Real-time alerts<br/>- Prediction charts]
        D3[Sites Management<br/>- Active sites display<br/>- Site status monitoring<br/>- Process tracking<br/>- Location mapping]
        D4[Device Management<br/>- Sensor configuration<br/>- Calibration status<br/>- Health monitoring<br/>- Maintenance alerts]
        D5[Reports & Analytics<br/>- Comprehensive reports<br/>- Multi-device analysis<br/>- Historical trends<br/>- Export functionality]
        D6[Prediction Interface<br/>- Real-time predictions<br/>- Risk visualization<br/>- Alert management<br/>- Decision support]
    end

    subgraph "Output Generation"
        E1[JSON Reports<br/>- Structured analysis results<br/>- Risk assessments<br/>- Performance metrics]
        E2[Visualization Files<br/>- 3D plots and heatmaps<br/>- Interactive dashboards<br/>- Risk maps]
        E3[CSV Logs<br/>- Trend analysis data<br/>- Historical tracking<br/>- Audit trails]
        E4[Raster Files<br/>- Geospatial risk maps<br/>- Coverage analysis<br/>- Spatial predictions]
    end

    subgraph "External Integrations"
        F1[Mining Control Systems<br/>- MineSight integration<br/>- Surpac connectivity<br/>- SCADA systems]
        F2[Cloud Services<br/>- Azure/AWS deployment<br/>- Data storage<br/>- Model serving]
        F3[IoT Networks<br/>- Real-time sensor feeds<br/>- Edge computing<br/>- Distributed processing]
        F4[Notification Systems<br/>- Email/SMS alerts<br/>- Emergency broadcasting<br/>- Stakeholder communication]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B3
    A4 --> B4
    A5 --> B5
    A6 --> B6
    A7 --> B7
    A8 --> B1
    A8 --> B2
    A8 --> B3

    B1 --> C2
    B2 --> C2
    B3 --> C2
    B4 --> C2
    B5 --> C2
    B6 --> C2
    B7 --> C2

    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5

    C5 --> D1
    C5 --> D2
    C5 --> D3
    C5 --> D4
    C5 --> D5
    C5 --> D6

    C3 --> E1
    C3 --> E2
    C3 --> E3
    C3 --> E4

    D5 --> F1
    D5 --> F2
    C5 --> F3
    C3 --> F4
```

## Detailed Data Flow Architecture

```mermaid
graph LR
    subgraph "Input Processing"
        I1[Raw Sensor Data] --> I2[Data Validation]
        I2 --> I3[Format Standardization]
        I3 --> I4[Quality Assessment]
    end

    subgraph "Analysis Pipeline"
        I4 --> P1[Parallel Processing]
        P1 --> P2[Feature Engineering]
        P2 --> P3[ML Model Inference]
        P3 --> P4[Risk Calculation]
        P4 --> P5[Result Aggregation]
    end

    subgraph "Storage & Caching"
        P5 --> S1[Redis Cache<br/>Real-time data]
        P5 --> S2[PostgreSQL<br/>Historical data]
        P5 --> S3[File System<br/>Large datasets]
    end

    subgraph "API Layer"
        S1 --> A1[REST APIs<br/>CRUD operations]
        S2 --> A2[GraphQL APIs<br/>Complex queries]
        S3 --> A3[File APIs<br/>Download/upload]
        A1 --> A4[WebSocket<br/>Real-time updates]
        A2 --> A4
        A3 --> A4
    end

    subgraph "Frontend Consumption"
        A4 --> F1[Dashboard Widgets<br/>Metrics & KPIs]
        A4 --> F2[Interactive Charts<br/>D3.js/Chart.js]
        A4 --> F3[Maps Integration<br/>Leaflet/OpenLayers]
        A4 --> F4[Real-time Alerts<br/>Toast notifications]
    end

    subgraph "Business Logic"
        F1 --> B1[Risk Assessment Engine<br/>Multi-factor analysis]
        F2 --> B2[Trend Analysis<br/>Time series forecasting]
        F3 --> B3[Spatial Analysis<br/>GIS operations]
        F4 --> B4[Alert Management<br/>Escalation rules]
    end

    B1 --> O1[Decision Support<br/>Operational recommendations]
    B2 --> O2[Predictive Insights<br/>Future risk projections]
    B3 --> O3[Site Optimization<br/>Resource allocation]
    B4 --> O4[Emergency Response<br/>Actionable alerts]
```

## Dashboard Metrics Flow Chart

```mermaid
graph TD
    subgraph "Real-time Metrics"
        M1[Active Sites Count<br/>24 sites] --> D1[Dashboard Cards]
        M2[Online Devices<br/>187 devices] --> D1
        M3[Daily Predictions<br/>42 predictions] --> D1
        M4[Critical Alerts<br/>3 active] --> D1
    end

    subgraph "Risk Distribution Charts"
        R1[Risk Level Breakdown<br/>Low/Medium/High/Critical] --> C1[Pie Chart]
        R2[Site-wise Risk Scores<br/>Heatmap] --> C2[Geographic Map]
        R3[Temporal Risk Trends<br/>Time series] --> C3[Line Chart]
        R4[Device Health Status<br/>Status indicators] --> C4[Status Dashboard]
    end

    subgraph "Prediction Performance"
        P1[Model Accuracy<br/>94% LiDAR, 89% overall] --> PC1[Performance Cards]
        P2[False Positive Rate<br/>3.2%] --> PC1
        P3[Prediction Coverage<br/>87% of highwall] --> PC1
        P4[Response Time<br/>< 2 seconds] --> PC1
    end

    subgraph "Operational KPIs"
        K1[MTBF - Mean Time Between Failures<br/>45 days] --> KC1[KPI Dashboard]
        K2[Alert Response Time<br/>8 minutes avg] --> KC1
        K3[Prevented Incidents<br/>12 this quarter] --> KC1
        K4[Cost Savings<br/>$2.5M annually] --> KC1
    end

    D1 --> UI1[Main Dashboard Grid]
    C1 --> UI2[Charts Section]
    C2 --> UI2
    C3 --> UI2
    C4 --> UI2
    PC1 --> UI3[Performance Section]
    KC1 --> UI4[KPI Section]

    UI1 --> UX1[Responsive Layout<br/>Mobile/Desktop]
    UI2 --> UX1
    UI3 --> UX1
    UI4 --> UX1
```

## Sites Management Flow Chart

```mermaid
graph TD
    subgraph "Site Data Sources"
        SD1[Site Configuration<br/>Location, boundaries, devices] --> SM1[Site Manager]
        SD2[Real-time Status<br/>Active/inactive processes] --> SM1
        SD3[Device Assignments<br/>Sensor mappings] --> SM1
        SD4[Analysis History<br/>Previous runs] --> SM1
    end

    subgraph "Site Processing Engine"
        SM1 --> SP1[Status Classification<br/>Active/Inactive/Pending]
        SP1 --> SP2[Process Monitoring<br/>Current analysis phase]
        SP2 --> SP3[Resource Allocation<br/>Compute assignment]
        SP3 --> SP4[Progress Tracking<br/>Completion percentage]
    end

    subgraph "Site Display Components"
        SP4 --> DC1[Site Cards Grid<br/>Status indicators]
        SP4 --> DC2[Active Sites Filter<br/>Currently processing]
        SP4 --> DC3[Progress Bars<br/>Analysis completion]
        SP4 --> DC4[Location Maps<br/>Geographic view]
    end

    subgraph "Interactive Features"
        DC1 --> IF1[Site Details Modal<br/>Device list, status]
        DC2 --> IF2[Bulk Operations<br/>Start/stop analysis]
        DC3 --> IF3[Real-time Updates<br/>WebSocket streaming]
        DC4 --> IF4[Geospatial Navigation<br/>Zoom, pan, filter]
    end

    subgraph "Site Operations"
        IF1 --> SO1[Device Management<br/>Add/remove sensors]
        IF2 --> SO2[Analysis Control<br/>Trigger processing]
        IF3 --> SO3[Status Monitoring<br/>Live updates]
        IF4 --> SO4[Site Configuration<br/>Boundary editing]
    end

    SO1 --> SM1
    SO2 --> SM1
    SO3 --> SM1
    SO4 --> SM1
```

## Comprehensive Report Generation Flow Chart

```mermaid
graph TD
    subgraph "Report Data Collection"
        RC1[Site Information<br/>Location, configuration, metadata] --> RA1[Report Aggregator]
        RC2[Device Analysis Results<br/>All sensor outputs] --> RA1
        RC3[Risk Assessments<br/>Individual and combined scores] --> RA1
        RC4[Historical Data<br/>Trend analysis] --> RA1
        RC5[Performance Metrics<br/>Model accuracy, coverage] --> RA1
    end

    subgraph "Report Processing Engine"
        RA1 --> RP1[Data Correlation<br/>Multi-sensor fusion]
        RP1 --> RP2[Risk Synthesis<br/>Overall assessment]
        RP2 --> RP3[Trend Analysis<br/>Historical patterns]
        RP3 --> RP4[Recommendation Engine<br/>Actionable insights]
        RP4 --> RP5[Visualization Generation<br/>Charts and maps]
    end

    subgraph "Report Components"
        RP5 --> RC6[Executive Summary<br/>Key findings, risks]
        RP5 --> RC7[Site Overview<br/>Location, devices, status]
        RP5 --> RC8[Detailed Analysis<br/>Per-device breakdowns]
        RP5 --> RC9[Risk Assessment<br/>Current and projected]
        RP5 --> RC10[Recommendations<br/>Mitigation strategies]
        RP5 --> RC11[Appendices<br/>Raw data, methodology]
    end

    subgraph "Report Formats"
        RC6 --> RF1[PDF Report<br/>Formatted document]
        RC7 --> RF1
        RC8 --> RF1
        RC9 --> RF1
        RC10 --> RF1
        RC11 --> RF1

        RC6 --> RF2[Interactive Dashboard<br/>Web-based view]
        RC7 --> RF2
        RC8 --> RF2
        RC9 --> RF2
        RC10 --> RF2

        RC6 --> RF3[JSON API<br/>Structured data]
        RC7 --> RF3
        RC8 --> RF3
        RC9 --> RF3
        RC10 --> RF3
    end

    subgraph "Report Distribution"
        RF1 --> RD1[Email Delivery<br/>Stakeholder notifications]
        RF1 --> RD2[Portal Access<br/>Web dashboard]
        RF1 --> RD3[API Integration<br/>External systems]

        RF2 --> RD4[Live Dashboard<br/>Real-time viewing]
        RF2 --> RD5[Embedded Reports<br/>iframe integration]

        RF3 --> RD6[Data Export<br/>Third-party tools]
        RF3 --> RD7[Analytics Integration<br/>BI platforms]
    end
```

## FastAPI Integration Architecture

```mermaid
graph TB
    subgraph "FastAPI Application"
        FA1[main.py<br/>Application entry point] --> FA2[API Router Configuration]
        FA2 --> FA3[CORS Middleware<br/>Frontend integration]
        FA3 --> FA4[Authentication Middleware<br/>JWT validation]
    end

    subgraph "API Endpoints"
        FA4 --> E1[POST /api/upload<br/>File upload endpoint]
        FA4 --> E2[GET /api/sites<br/>Sites listing]
        FA4 --> E3[GET /api/dashboard/metrics<br/>Dashboard data]
        FA4 --> E4[POST /api/analysis/start<br/>Trigger analysis]
        FA4 --> E5[GET /api/reports/{site_id}<br/>Report generation]
        FA4 --> E6[WebSocket /ws/updates<br/>Real-time updates]
    end

    subgraph "Business Logic Layer"
        E1 --> BL1[File Processing Service<br/>Validation, storage]
        E2 --> BL2[Site Management Service<br/>CRUD operations]
        E3 --> BL3[Metrics Calculation Service<br/>Aggregation logic]
        E4 --> BL4[Analysis Orchestration<br/>Notebook execution]
        E5 --> BL5[Report Generation Service<br/>PDF/JSON creation]
        E6 --> BL6[WebSocket Manager<br/>Real-time broadcasting]
    end

    subgraph "Data Access Layer"
        BL1 --> DA1[File System Handler<br/>Upload directory management]
        BL2 --> DA2[PostgreSQL Models<br/>Site, Device tables]
        BL3 --> DA3[Redis Cache<br/>Metrics caching]
        BL4 --> DA4[Jupyter Client<br/>Notebook execution]
        BL5 --> DA5[Template Engine<br/>Report formatting]
        BL6 --> DA6[WebSocket Connections<br/>Client management]
    end

    subgraph "External Dependencies"
        DA1 --> EX1[Local File System<br/>Data persistence]
        DA2 --> EX2[PostgreSQL Database<br/>Relational data]
        DA3 --> EX3[Redis Cache<br/>High-performance cache]
        DA4 --> EX4[Jupyter Kernel Gateway<br/>Analysis execution]
        DA5 --> EX5[Jinja2 Templates<br/>Report templates]
        DA6 --> EX6[WebSocket Protocol<br/>Real-time communication]
    end

    subgraph "Background Tasks"
        EX4 --> BT1[Celery Workers<br/>Async processing]
        BT1 --> BT2[Analysis Queue<br/>Job management]
        BT2 --> BT3[Result Processing<br/>Output handling]
        BT3 --> BT4[Notification Service<br/>Alert dispatching]
    end
```

## Complete System Integration Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend (React)
    participant A as FastAPI Backend
    participant J as Jupyter Notebooks
    participant D as Database (PostgreSQL)
    participant R as Redis Cache
    participant FS as File System

    U->>F: Login Request
    F->>A: POST /api/auth/login
    A->>D: Validate credentials
    D-->>A: JWT Token
    A-->>F: Authentication success
    F-->>U: Dashboard access

    U->>F: Upload sensor data
    F->>A: POST /api/upload
    A->>FS: Store files
    A->>D: Log upload event
    A-->>F: Upload confirmation

    U->>F: Start analysis
    F->>A: POST /api/analysis/start
    A->>J: Execute notebooks
    J->>FS: Generate outputs
    J-->>A: Analysis complete
    A->>D: Store results
    A->>R: Cache metrics
    A-->>F: Analysis status

    F->>A: GET /api/dashboard/metrics
    A->>R: Fetch cached data
    R-->>A: Metrics data
    A-->>F: Dashboard data
    F-->>U: Render charts

    U->>F: View sites page
    F->>A: GET /api/sites
    A->>D: Query active sites
    D-->>A: Sites data
    A-->>F: Sites list
    F-->>U: Display active sites

    U->>F: Generate report
    F->>A: GET /api/reports/{site_id}
    A->>D: Fetch site data
    A->>FS: Gather analysis files
    A->>A: Aggregate results
    A-->>F: Comprehensive report
    F-->>U: Display report

    A->>F: WebSocket updates
    F-->>U: Real-time notifications
```

## Technology Stack Integration

```mermaid
graph TB
    subgraph "Frontend Stack"
        R1[React 19.1.1<br/>Component framework]
        R2[Vite<br/>Build tool]
        R3[Tailwind CSS<br/>Styling]
        R4[React Router<br/>Navigation]
        R5[Axios<br/>HTTP client]
        R6[Chart.js/D3.js<br/>Data visualization]
        R7[Leaflet<br/>Maps integration]
    end

    subgraph "Backend Stack"
        P1[FastAPI<br/>Web framework]
        P2[Uvicorn<br/>ASGI server]
        P3[SQLAlchemy<br/>ORM]
        P4[Alembic<br/>Database migrations]
        P5[Pydantic<br/>Data validation]
        P6[Celery<br/>Task queue]
        P7[Redis<br/>Caching & sessions]
    end

    subgraph "Data Science Stack"
        J1[Jupyter Notebook<br/>Analysis environment]
        J2[NumPy/Pandas<br/>Data processing]
        J3[Scikit-learn<br/>Machine learning]
        J4[Plotly<br/>Visualization]
        J5[Open3D<br/>3D processing]
        J6[Rasterio<br/>Geospatial]
        J7[PyVista<br/>3D visualization]
    end

    subgraph "Infrastructure"
        I1[Docker<br/>Containerization]
        I2[PostgreSQL<br/>Primary database]
        I3[Redis<br/>Cache & queues]
        I4[Nginx<br/>Reverse proxy]
        I5[MinIO<br/>Object storage]
        I6[Prometheus<br/>Monitoring]
    end

    subgraph "External Services"
        E1[Azure/AWS<br/>Cloud deployment]
        E2[SendGrid<br/>Email notifications]
        E3[Twilio<br/>SMS alerts]
        E4[MineSight API<br/>Mining software integration]
        E5[Weather APIs<br/>Environmental data]
    end

    R1 --> P1
    R2 --> P1
    R3 --> R1
    R4 --> R1
    R5 --> P1
    R6 --> R1
    R7 --> R1

    P1 --> J1
    P2 --> P1
    P3 --> P1
    P4 --> P3
    P5 --> P1
    P6 --> P1
    P7 --> P1

    J1 --> J2
    J2 --> J3
    J3 --> J4
    J4 --> J5
    J5 --> J6
    J6 --> J7

    P1 --> I1
    I1 --> I2
    I1 --> I3
    I1 --> I4
    I1 --> I5
    I1 --> I6

    I2 --> E1
    I3 --> E1
    P1 --> E2
    P1 --> E3
    P1 --> E4
    P1 --> E5
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV1[Local Development<br/>VS Code + Extensions]
        DEV2[Docker Compose<br/>Local services]
        DEV3[Jupyter Lab<br/>Analysis development]
        DEV4[Git<br/>Version control]
    end

    subgraph "CI/CD Pipeline"
        CI1[GitHub Actions<br/>Automated testing]
        CI2[Docker Build<br/>Container creation]
        CI3[Security Scan<br/>Vulnerability check]
        CI4[Performance Test<br/>Load testing]
    end

    subgraph "Staging Environment"
        STG1[Azure Container Apps<br/>Backend deployment]
        STG2[Azure Database<br/>PostgreSQL]
        STG3[Azure Cache<br/>Redis]
        STG4[Azure Storage<br/>File storage]
    end

    subgraph "Production Environment"
        PROD1[Azure Kubernetes Service<br/>Scalable deployment]
        PROD2[Azure Database<br/>High availability]
        PROD3[Azure Redis<br/>Enterprise cache]
        PROD4[Azure Blob Storage<br/>Global CDN]
        PROD5[Azure Front Door<br/>Load balancing]
    end

    subgraph "Monitoring & Observability"
        MON1[Azure Application Insights<br/>Performance monitoring]
        MON2[Azure Log Analytics<br/>Centralized logging]
        MON3[Azure Monitor<br/>Infrastructure metrics]
        MON4[Prometheus/Grafana<br/>Custom dashboards]
    end

    DEV1 --> CI1
    DEV2 --> CI1
    DEV3 --> CI1
    DEV4 --> CI1

    CI1 --> CI2
    CI2 --> CI3
    CI3 --> CI4
    CI4 --> STG1

    STG1 --> PROD1
    STG2 --> PROD2
    STG3 --> PROD3
    STG4 --> PROD4

    PROD1 --> MON1
    PROD2 --> MON2
    PROD3 --> MON3
    PROD4 --> MON4

    MON1 --> PROD5
    MON2 --> PROD5
    MON3 --> PROD5
    MON4 --> PROD5
```

This comprehensive flow chart architecture provides a complete blueprint for the AI Rockfall Prediction System, incorporating FastAPI integration, enhanced dashboard with metrics and charts, sites management showing active processes, and comprehensive reporting combining all device analyses.</content>
<parameter name="filePath">c:\Users\rkste\Desktop\AI Rockfall Prediction\SYSTEM_ARCHITECTURE_FLOWCHART.md