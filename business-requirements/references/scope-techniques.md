# Scope Representation Techniques

Visual models help define the boundary between what is inside the system and everything else in the universe. Use Mermaid syntax for quick illustrations styled for **Xray.tech**.

## 1. Context Diagram
**Purpose:** Illustrates the system's boundary and connections to external entities.

```mermaid
graph LR
    %% Xray Branding - Urbanist (Headings) & Figtree (Body)
    classDef system fill:#1D2639,stroke:#1D2639,color:#fff,rx:20,ry:20;
    classDef actor fill:#fff,stroke:#1D2639,color:#1D2639,rx:15,ry:15;
    classDef highlight fill:#3B71FE,stroke:#3B71FE,color:#fff,rx:15,ry:15;

    subgraph Boundary
        System((Chemical Tracking System)):::system
    end
    
    Chemist[Chemist]:::actor -- Chemical Request --> System
    System -- Chemical Container --> Chemist
    Buyer[Buyer]:::actor -- Order Details --> System
    System -- Reporting Data --> HealthSafety[Health & Safety Dept]:::highlight
    Scanner[Bar Code Reader]:::actor -- Scan Data --> System
```

## 2. Ecosystem Map
**Purpose:** Shows all systems related to the system of interest, including indirect interactions.

```mermaid
graph TD
    %% Xray Branding
    classDef main fill:#1D2639,stroke:#1D2639,color:#fff,rx:20,ry:20;
    classDef support fill:#fff,stroke:#1D2639,color:#1D2639,rx:15,ry:15;
    classDef external fill:#FF6B4A,stroke:#FF6B4A,color:#fff,rx:15,ry:15;

    CTS[<b>Chemical Tracking System</b>]:::main
    PS[Purchasing System]:::support
    RS[Receiving System]:::support
    HSID[Health & Safety Incident Database]:::support
    CTD[Corporate Training Database]:::support
    OSHA[OSHA/EPA Reporting Interface]:::external

    PS <--> CTS
    RS --> CTS
    CTD -- Training Records --> CTS
    CTS -- Incident Data --> HSID
    HSID --> OSHA
```

## 3. Feature Tree (Pretty Tree Structure)
**Purpose:** A hierarchical depiction of product features.

```mermaid
graph LR
    %% Xray Branding - Tree Layout
    classDef root fill:#1D2639,stroke:#1D2639,color:#fff,rx:20,ry:20,font-size:16px;
    classDef l1 fill:#3B71FE,stroke:#3B71FE,color:#fff,rx:15,ry:15;
    classDef l2 fill:#fff,stroke:#1D2639,color:#1D2639,rx:10,ry:10;
    classDef l3 fill:none,stroke:none,color:#1D2639,font-style:italic;

    Root((Chemical Tracking System)):::root
    
    %% Level 1
    OC[Order Chemicals]:::l1
    IM[Inventory Management]:::l1
    RR[Regulatory Reporting]:::l1
    
    Root --- OC
    Root --- IM
    Root --- RR
    
    %% Level 2 - Order Chemicals
    OCS[Search]:::l2
    OCR[Chemical Request]:::l2
    OC --- OCS
    OC --- OCR
    
    %% Level 3 - Search
    OCSL[Local Lab Search]:::l3
    OCSV[Vendor Catalog Search]:::l3
    OCS --- OCSL
    OCS --- OCSV
    
    %% Level 2 - Inventory Management
    IMT[Track Container Location]:::l2
    IMU[Update Quantity]:::l2
    IM --- IMT
    IM --- IMU
    
    %% Level 2 - Regulatory Reporting
    RRH[Hazardous Material Reports]:::l2
    RRD[Disposal History]:::l2
    RR --- RRH
    RR --- RRD
```

## 4. Event List
**Purpose:** Identifies external triggers.

```mermaid
flowchart LR
    %% Xray Branding
    classDef trigger fill:#fff,stroke:#3B71FE,color:#3B71FE,rx:15,ry:15,stroke-width:2px;
    classDef system fill:#1D2639,stroke:#1D2639,color:#fff,rx:20,ry:20;
    classDef response fill:#3B71FE,stroke:#3B71FE,color:#fff,rx:15,ry:15;

    E1[User: Request Chemical]:::trigger --> System((System)):::system
    E2[Temporal: Monthly Report]:::trigger --> System
    E3[Signal: Scan Container]:::trigger --> System
    System --> R1[Response: Update Inventory]:::response
```

### Note on Rendering with Fonts
To render these diagrams with **Urbanist** and **Figtree** fonts using `mermaid-cli` (`mmdc`), provide a CSS file with the following `@import` and font-family rules:

```css
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;700&family=Figtree:wght@400;700&display=swap');
text, .label, .nodeText { font-family: 'Figtree', sans-serif !important; }
.root text, h1, h2, h3, b { font-family: 'Urbanist', sans-serif !important; }
```

Render command: `mmdc -i input.mmd -o output.png -C diagrams/style.css`
