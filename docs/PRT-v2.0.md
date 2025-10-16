# Product Requirements Template (PRT)
**Project Name**: Glossary Extraction & Validation App  
**Objective**:  
Develop a guided software tool that extracts, validates, compares, and translates glossary entries from internal technical documents (German and English), resulting in a clean bilingual glossary aligned with international standards and "gold standard" sources (NAMUR, DIN, ASME). A Neo4j graph database visualizes term-standard relationships to enhance validation and analysis.

## 1. Purpose
The application supports engineering and documentation teams in extracting, validating, and harmonizing bilingual terminology from internal technical standards. It addresses misleading translations, inconsistent terminology, and non-standard language by guiding users through a structured workflow. The resulting glossary aligns with international references (IEC Electropedia, IEV-Wörterbuch, IATE) and authoritative "gold standards" (NAMUR, DIN, ASME), with Neo4j enabling visualization of term-standard relationships for compliance and analysis.

## 2. Scope
**Included**:
- Upload and process German and English documents independently
- Import NAMUR, DIN, ASME, and other standards (PDF/TBX files) as gold standards via GUI
- Extract glossary entries using NLP or rule-based logic
- Validate entries manually and via external databases or gold standards
- Translate missing entries where only one language is available
- Compare and merge bilingual entries, prioritizing gold standards
- Visualize term-standard relationships in a Neo4j graph
- Export final glossary to standard formats (CSV, Excel, JSON, XML)
**Not Included (Initial Version)**:
- Real-time collaboration or cloud sync
- Automatic glossary generation without user validation
- Full integration with enterprise systems (e.g., SharePoint)

## 3. Functional Requirements
**Document Ingestion Module**  
- Upload German and/or English PDF documents (support text-based and scanned PDFs via OCR; handle tables/multi-columns)
- Import NAMUR, DIN, ASME, and other standards (PDF/TBX) as gold standards via GUI
- Extract raw text using PDF parsing libraries or TBX parsers  
**Glossary Extraction Module**  
- Detect term-definition pairs using NLP (e.g., for unstructured text) or rule-based logic (e.g., for structured sections like headings)
- Store entries in separate German and English source tables and Neo4j graph  
**Validation Module**  
- Manual review of glossary entries (side-by-side comparison with external matches or NAMUR/DIN/ASME gold standards)
- Lookup and validation against IEC Electropedia, IEV-Wörterbuch, IATE, cached gold standards, and Neo4j relationships
- Mark entries as “validated” before matching  
**Translation Module**  
- Identify entries that exist in only one language
- Translate missing terms using DeepL or Microsoft Translator (with fallback to manual input or gold standards)
- Allow manual review and correction of translations  
**Glossary Comparison Module**  
- Match validated German and English entries, prioritizing NAMUR/DIN/ASME gold standards and Neo4j relationships
- Flag inconsistent or misleading translations
- Suggest corrections or allow manual resolution  
**Glossary Builder Module**  
- Merge validated entries into a bilingual glossary, favoring gold standard terms
- Export to CSV, Excel, JSON, or XML (TBX-compliant)
- Optionally store locally or in internal repositories  
**Graph Visualization Module**  
- Populate Neo4j with Term and Standard nodes, linked by relationships (e.g., DEFINED_BY, SYNONYM)
- Display interactive graph in GUI (nodes: terms/standards; edges: relationships)
- Support queries like “Show terms linked to ASME”  
**Error Handling & Logging**  
- Handle failed uploads, parsing errors, API failures, and Neo4j connectivity gracefully (e.g., offline mocks)
- Log user actions, system events, and graph updates for audit and debugging

## 4. Non-Functional Requirements
- **Usability**: Intuitive UI with a dark theme (default) for technical users, with minimal training (e.g., complete workflow in <10 min after 30-min tutorial). Support customizable dialog background colors via a Settings interface, company logo upload (PNG), WCAG 2.1 AA compliance (contrast ratios ≥4.5:1), and interactive graph visualization. Include progress indicators for long tasks (e.g., PDF/TBX parsing, graph population, exports).
- **Performance**: Process 100-page PDFs in <60 sec; handle up to 1,000 glossary entries; Neo4j queries return in <2 sec for 10,000 nodes.
- **Reliability**: Ensure glossary and graph integrity during edits and exports
- **Extensibility**: Modular design for future enhancements
- **Offline Capability**: Operate without mandatory cloud dependencies (use local mocks, TerminologyCache, Neo4j caching)
- **Security**: Local file encryption (AES-256), access control (OAuth/role-based), secure Neo4j access
- **Compliance**: GDPR or internal data handling policies

## 5. Advanced Features
- AI-driven term suggestions (e.g., auto-complete from external DBs or NAMUR/DIN/ASME)
- Batch processing for multiple documents
- User feedback loop (flag incorrect entries, rate translations)
- Domain-specific profiles (filter/prioritize terms by engineering domains)
- Graph-based analytics (e.g., “Find terms shared by DIN and ASME”)

## 6. User Roles
- **Editor**: Upload documents, import gold standards, extract/edit glossary entries, manage graph
- **Reviewer**: Validate entries, comment on translations, view graph
- **Viewer**: View and export final glossary, view graph

**Permissions Matrix**:

| Role     | Upload/Extract/Import Standards | Edit Entries | Validate/Comment | View/Export/Graph |
|----------|--------------------------------|--------------|------------------|-------------------|
| Editor   | Yes                            | Yes          | Yes              | Yes               |
| Reviewer | No                             | No           | Yes              | Yes               |
| Viewer   | No                             | No           | No               | Yes               |

## 7. Technology Stack
- **Frontend**: React (Material-UI for dark theme; react-dropzone for PDF/TBX uploads; react-image for logo PNG; vis.js/Reagraph for graph visualization)
- **Backend**: FastAPI (Python 3.10+)
- **Data**: SQLite or H2 (glossary storage, TerminologyCache; CSV/Excel for exports); Neo4j Community Edition (term-standard relationships)
- **PDF Parsing**: PyPDF2 or pdfplumber (text), Tesseract for OCR (scanned)
- **TBX Parsing**: lxml (for NAMUR/DIN/ASME TBX imports)
- **NLP**: spaCy (term extraction, fuzzy matching)
- **Translation/Validation**: DeepL/Microsoft Translator APIs, requests for IATE/IEC
- **Graph DB**: Neo4j (neo4j-driver for queries, Cypher for graph operations)
- **Testing**: pytest (backend), Jest (frontend), Cypress (E2E), axe-core (accessibility)
- **Dependencies**: numpy, exposed (if H2), styled-components (UI customization), neo4j-driver
- **AI Integration**: Claude AI (via API/desktop app) for code generation; MCP for file/DB access; Cursor, Aider, Zed, or VS Code with Claude extension
- **Browser Integration**: Microsoft Edge Web MCP extension for web-based automation (e.g., terminology lookups)

## 8. Workflow Summary
- Upload German Document → Extract & Validate German Glossary
- Upload English Document (Optional) → Extract & Validate English Glossary
- Import NAMUR/DIN/ASME Standards via GUI → Cache as Gold Standards and Populate Neo4j
- Translate missing entries
- Match and compare validated entries, prioritizing gold standards and graph relationships
- Visualize term-standard relationships in GUI
- Review inconsistencies and finalize glossary
- Export or store glossary

**Text-Based Workflow Diagram**:
```
[Start] --> [Upload PDF (de/en) or NAMUR/DIN/ASME] --> [Parse Text (PyPDF2/OCR/TBX)]
          |
          v
[Extract Terms (spaCy/rules)] --> [Store in DB/Cache (SQLite/H2) & Neo4j]
          |
          v
[Manual Validate (side-by-side w/ NAMUR/DIN/ASME/IATE)] --> [Translate Missing (DeepL)]
          |
          v
[Compare/Merge (flag inconsistencies, prioritize gold)] --> [Visualize Graph (Neo4j)]
          |
          v
[Build Glossary] --> [Export (TBX/CSV)]
          |
          v
[End: Audit Log]
```

## 9. Data Model Overview
**GlossaryEntry (SQLite)**  
- Attributes: id, term, definition, language, source_document, creation_date, domain_tags, validation_status (pending/validated), source ('internal', 'NAMUR', 'DIN', 'ASME')  
**GlossaryMatch (SQLite)**  
- Attributes: de_entry_id, en_entry_id, match_quality (score), inconsistency_flags, source_priority (1.5 for NAMUR/DIN/ASME)  
**GlossaryVersion (SQLite)**  
- Attributes: version_id, timestamp, changes_summary, user_id  
**TerminologyCache (SQLite)**  
- Attributes: term, definition, language, source ('NAMUR', 'DIN', 'ASME'), last_updated  
**Graph Model (Neo4j)**  
- **Nodes**:
  - Term: id, term, definition, language, validation_status, domain_tags
  - Standard: id, name (e.g., 'ASME Y14.5'), version, file_source
- **Relationships**:
  - DEFINED_BY: (Term)-[:DEFINED_BY]->(Standard)
  - SYNONYM: (Term)-[:SYNONYM]->(Term)
  - DOMAIN: (Term)-[:DOMAIN]->(Domain)
- **Sync**: Term nodes sync with GlossaryEntry via id; Standard nodes from uploaded files  
**Relationships**:  
- One GlossaryEntry can link to another via GlossaryMatch  
- Multiple GlossaryEntry records belong to one GlossaryVersion  
- Term nodes can have multiple DEFINED_BY, SYNONYM, DOMAIN relationships  
**Storage Limits**: Max 10,000 glossary entries (SQLite); retain 10 versions; cache 50,000 gold standard terms (SQLite); Neo4j supports 10,000 Term nodes, 100 Standard nodes

## 10. System Architecture Overview
The app is a modular, extensible system guiding users through glossary extraction, validation, translation, merging, and visualization of term-standard relationships. It uses FastAPI, React, SQLite/H2, and Neo4j, ensuring clarity, maintainability, and scalability.

**Frontend Layer**  
- **Technology**: React  
- **Features**:  
  - File upload (react-dropzone for PDFs/TBX)  
  - Gold standard import via Settings UI (NAMUR/DIN/ASME)  
  - Glossary review/editing with dark theme (Material-UI)  
  - Validation/translation controls (side-by-side with gold standards)  
  - Graph visualization (vis.js/Reagraph for Neo4j)  
  - Export options (CSV, Excel, JSON, TBX)  
  - Logo upload (PNG, header/settings)  
  - Settings for dialog colors and standards import  
  - Progress indicators for parsing/graph/exports  
  - WCAG 2.1 AA compliance  

**Backend Layer**  
- **Technology**: FastAPI  
- **Modules**:  
  - PDF Parser: Extracts text from documents and NAMUR/DIN/ASME PDFs  
  - TBX Parser: Parses NAMUR/DIN/ASME TBX files  
  - Glossary Extractor: Identifies term-definition pairs (NLP/rules)  
  - Validator: Checks terms against IEC, IATE, cached gold standards, Neo4j  
  - Translator: Uses DeepL/Microsoft Translator for missing entries  
  - Glossary Matcher: Links de/en terms, prioritizes gold standards/graph  
  - Glossary Builder: Merges entries into bilingual glossary  
  - Graph Manager: Populates/queries Neo4j for term-standard relationships  

**Data Layer**  
- **Technology**: SQLite or H2; Neo4j  
- **Entities**: GlossaryEntry, GlossaryMatch, GlossaryVersion, TerminologyCache (SQLite); Term, Standard nodes (Neo4j)  
- **Purpose**: Stores glossary data, versions, cached gold standards, and graph relationships  

**Integration Layer**  
- **Services**: IEC Electropedia, IEV-Wörterbuch, IATE, DeepL, Microsoft Translator, NAMUR/DIN/ASME (PDF/TBX), Neo4j  
- **Features**: Handle rate limits with offline caching (TerminologyCache, Neo4j)  

**Data Flow**  
- Upload documents/standards → Parse terms → Store in SQLite/Neo4j  
- Validate against gold standards/Neo4j → Translate missing terms  
- Match bilingual terms, prioritize gold standards/graph → Visualize relationships  
- Merge and export glossary  

**Design Principles**  
- Modularity: Independent, reusable modules  
- Transparency: Traceable entries and relationships (metadata, versions)  
- User Control: Manual review for validation/translation  
- Scalability: Supports enhancements (e.g., clustering, domains)  

**Deployment**  
- Hybrid (local default, cloud optional)  
- Requirements: Python 3.10+, Node.js, Neo4j Community Edition  
- Updates: Manual or via package manager  

## 11. Development Guidelines
- **Single Responsibility**: Each module does one task well
- **Loose Coupling**: Minimize inter-module dependencies
- **Clear Interfaces**: Well-defined APIs/functions
- **Test Isolation**: Mock dependencies for unit tests
- **Code Reusability**: Utility modules for shared logic
- **Documentation**: Docstrings and usage examples
- **AI-Assisted Coding**: Use Claude for modular code, ISO/Neo4j alignment; review manually
- **Tool Integration**: MCP for Claude to access files (PDF/TBX), databases (SQLite/Neo4j), APIs

## 12. Development Phases
- Phase 1: Document Ingestion & Extraction (2 weeks)
- Phase 2: Validation, Translation & Graph Setup (3.5 weeks)
- Phase 3: Comparison & Builder (2 weeks)
- Phase 4: Testing & Polish (2.5 weeks)

## 13. Unit Testing & CI/CD Integration
- Block merges if coverage < threshold
- Run tests on every commit/pull request
- **Test Types**: Unit (pytest), integration, E2E (Cypress), accessibility (axe-core), mutation (mutmut)
- **Coverage**: ≥90% for critical modules (glossary/graph integrity); ≥80% for core logic
- **Goals**: Ensure correctness, catch regressions, support CI/CD

## 14. Unit Testing Strategy
- TBX Compliance: Validate exports against ISO 30042
- Accessibility: WCAG 2.1 AA via axe-core
- Gold Standard: Verify NAMUR/DIN/ASME parsing/validation
- Graph: Test Neo4j node/relationship creation and queries

## 15. Future Enhancements
- User feedback loop (flag/rate entries)
- Domain-specific profiles
- Glossary consistency checker
- Plugin/API mode (e.g., SharePoint, COMOS)
- Graph analytics (e.g., cross-standard term analysis)
- Additional languages
- Change impact analysis
- Governance workflow (draft-review-approve)
- Full theme editor
- Browser automation via MCP
- AI-powered term clustering (Chroma/Vectara)
- Voice-controlled UI
- Glossary diff viewer

## 16. Development Team Roles
- Python Developer: Core logic, Neo4j integration
- NLP Specialist: Term extraction algorithms
- Database Engineer: SQLite/H2 and Neo4j schemas
- Unit Testing Engineer: Test suites
- React Frontend Developer: UI, graph visualization
- Integration Engineer: APIs, gold standards, Neo4j
- DevOps Engineer: CI/CD, deployment, Neo4j setup
- Project Coordinator: Oversees progress

## 17. Agentic Development Strategy
- **Principles**: Task decomposition, agent handoff protocols, testing contracts, agent registry, traceability
- **Claude Integration**: Use Claude for code generation (prompts per Section 18); MCP for file/DB access (Filesystem, SQLite, Neo4j); tools like Cursor, Aider, Zed
- **MCP Servers**:
  - Filesystem: PDF/TBX/logo handling
  - SQLite: Glossary/cache queries
  - Neo4j: Graph queries
  - Git: Versioning
  - Fetch/Puppeteer: Fallback for terminology lookups
  - Others (e.g., Sentry, Chroma) for monitoring/enhancements

## 18. Implementation Plan
Agile methodology with granular steps (1-2 days, ~1k-2k tokens for Claude). Total timeline: 10 weeks.

**Phase 1: Document Ingestion & Extraction (Weeks 1-2)**  
- **Step 1.1.1**: Initialize FastAPI repo (app.py, /health endpoint, neo4j-driver)  
  - **Prompt**: "Create FastAPI app skeleton with /health endpoint, include neo4j-driver (Section 7)."  
  - **Tests**: Pytest (status 200)  
- **Step 1.1.2**: Setup SQLite/H2 (GlossaryEntry, TerminologyCache) and Neo4j (Term, Standard nodes)  
  - **Prompt**: "Implement SQLAlchemy models for GlossaryEntry/TerminologyCache and Neo4j schema for Term/Standard nodes (Section 9)."  
  - **Tests**: Unit tests for model creation/query  
- **Step 1.2.1**: Add /upload-pdf, /upload-tbx endpoints (tag gold standards)  
  - **Prompt**: "Add FastAPI endpoints for PDF/TBX upload, store locally, tag gold standards, include progress updates."  
  - **Tests**: Integration test with mock files  
- **Step 1.2.2**: Implement text extraction (PyPDF2, lxml, Tesseract)  
  - **Prompt**: "Write function to extract text from PDF (PyPDF2) and TBX (lxml), with OCR fallback."  
  - **Tests**: Pytest with sample PDFs/TBX  
- **Step 1.3.1**: NLP extraction (spaCy)  
  - **Prompt**: "Using spaCy, create term-definition pair extractor for unstructured text."  
  - **Tests**: Unit tests for extraction rules  
- **Step 1.3.2**: Store terms in SQLite/Neo4j  
  - **Prompt**: "Connect extractor to DB: Save document terms as GlossaryEntry, gold standards as TerminologyCache, populate Neo4j Term/Standard nodes with DEFINED_BY relationships."  
  - **Tests**: Integration tests (text → DB/Neo4j)  
- **Milestone 1**: Upload PDFs/TBX, verify extraction in DB/Neo4j, check progress indicators (coverage ≥80%)

**Phase 2: Validation, Translation & Graph Setup (Weeks 3-5.5)**  
- **Step 2.1.1**: Add /validate-term endpoint (query TerminologyCache/Neo4j, mock APIs)  
  - **Prompt**: "Implement FastAPI endpoint to mark terms as validated, query TerminologyCache/Neo4j for NAMUR/DIN/ASME, mock IATE lookup."  
  - **Tests**: Pytest with mocks/cache/Neo4j queries  
- **Step 2.1.2**: Integrate IATE/DeepL APIs, TerminologyCache/Neo4j  
  - **Prompt**: "Add requests-based client for IATE, handle errors, prioritize TerminologyCache/Neo4j for NAMUR/DIN/ASME."  
  - **Tests**: Integration tests with mocks  
- **Step 2.2.1**: Translation logic (DeepL, gold standard fallback)  
  - **Prompt**: "Create function to translate missing terms using DeepL, fallback to NAMUR/DIN/ASME cache or manual input."  
  - **Tests**: Unit tests for translation  
- **Step 2.2.2**: Manual correction UI integration  
  - **Prompt**: "Integrate translation with DB and Neo4j updates for corrections."  
  - **Tests**: Integration tests for translation flow  
- **Step 2.3.1**: Setup React app (Material-UI, vis.js/Reagraph, WCAG)  
  - **Prompt**: "Generate React boilerplate with Material-UI dark theme, vis.js for graph visualization, WCAG-compliant."  
  - **Tests**: Jest for theme/graph; axe-core  
- **Step 2.3.2**: Add upload/validation/graph views  
  - **Prompt**: "Create React component for term validation with API fetch, gold standard matches, and Neo4j graph visualization."  
  - **Tests**: React Testing Library  
- **Step 2.3.3**: Settings UI (color picker, logo upload, gold standard import)  
  - **Prompt**: "Add Settings component with color picker, PNG logo upload, TBX/PDF gold standard import, WCAG-compliant."  
  - **Tests**: Jest for state; axe-core  
- **Step 2.3.4**: Neo4j query endpoint and graph UI  
  - **Prompt**: "Generate FastAPI endpoint and React component for Neo4j term-standard graph visualization (Section 9)."  
  - **Tests**: Pytest for endpoint; Jest for graph  
- **Milestone 2**: Validate/translate terms, import gold standards, view graph, verify accessibility (coverage ≥80%)

**Phase 3: Comparison & Builder (Weeks 6-7)**  
- **Step 3.1.1**: Matching logic (prioritize gold standards/Neo4j)  
  - **Prompt**: "Implement term matching algorithm for de/en pairs, prioritizing NAMUR/DIN/ASME and Neo4j relationships."  
  - **Tests**: Pytest for match quality  
- **Step 3.1.2**: Builder/export (TBX XML)  
  - **Prompt**: "Create TBX-compliant XML exporter from DB."  
  - **Tests**: Schema validation tests  
- **Step 3.2.1**: Comparison views (flags, progress indicators)  
  - **Prompt**: "Build React view for glossary comparison with flags, progress bar, NAMUR/DIN/ASME/Neo4j prioritization."  
  - **Tests**: Jest for rendering  
- **Step 3.2.2**: Export UI (format buttons)  
  - **Prompt**: "Add export buttons in React, calling backend, with progress indicators."  
  - **Tests**: E2E for export flow  
- **Milestone 3**: Compare/merge, export files, verify graph compliance (coverage ≥85%)

**Phase 4: Testing & Polish (Weeks 8-10)**  
- **Step 4.1.1**: Unit tests for all modules (include Neo4j)  
  - **Prompt**: "Generate Pytest for PDF/TBX Parser and Neo4j Graph Manager, including NAMUR/DIN/ASME parsing and Cypher queries."  
  - **Tests**: Pytest suite; mutation (mutmut)  
- **Step 4.1.2**: Integration/E2E tests (Cypress for UI/graph)  
  - **Prompt**: "Create Cypress tests for upload-validate-export-graph workflow with NAMUR/DIN/ASME import."  
  - **Tests**: CI/CD run  
- **Step 4.2.1**: Polish UI (dark theme, WCAG, graph enhancements)  
  - **Prompt**: "Refactor React for better dark mode contrast, WCAG-compliant, with enhanced Neo4j graph visualization."  
  - **Tests**: Axe-core in Jest  
- **Step 4.2.2**: Optimize performance (chunked parsing, Neo4j queries)  
  - **Prompt**: "Optimize extraction for large PDFs/TBX and Neo4j queries for 10,000 nodes."  
  - **Tests**: Performance tests  
- **Step 4.3.1**: Error handling/logs (gold standards, Neo4j)  
  - **Prompt**: "Implement structured logging for all endpoints, including gold standard import and Neo4j errors."  
  - **Tests**: Tests for error paths  
- **Step 4.3.2**: Deployment (Docker, Neo4j)  
  - **Prompt**: "Create Docker setup for FastAPI/React app with Neo4j Community Edition."  
  - **Tests**: Smoke tests in container  
- **Milestone 4**: Full app walkthrough; verify customs/theme/offline/cache/accessibility/graph (coverage ≥85%)

**Post-Implementation**  
- **Retrospective (Week 11)**: Review; plan enhancements (Section 15)  
- **Monitoring**: Sentry (MCP) for logs

## 20. Standards Alignment
**ISO Standards**:  
- ISO 26162-1:2019, 26162-2:2019, 26162-3:2023 (terminology DBs)  
- ISO 30042:2019 (TBX)  
- ISO 12620:2019 (data categories)  
- ISO 704:2022 (concept systems, aligned with NAMUR/DIN/ASME/Neo4j)  
- Others: ISO 1087, 860, 10241-1/2, 12199, 12200, 6156  
**Gold Standards**: NAMUR, DIN, ASME (e.g., Y14.5, B31.3)  
**TBX Compliance**: TBX-Core, XML export, ISO 12620 metadata, multilingual entries  
**Graph Compliance**: Neo4j relationships align with ISO 704 (e.g., DEFINED_BY)

## 21. Stakeholder List
- Engineering Teams: Term extraction/validation/graph visualization
- Documentation Teams: Glossary accuracy
- Project Sponsors: Standards alignment
- IT/Security: GDPR, Neo4j security
- Consultants: NLP/standards/graph DB expertise

## 22. Risk Assessment
- **NLP Accuracy**: Mitigate with hybrid NLP/rules, manual review, Neo4j validation
- **API Downtime**: Offline mocks, TerminologyCache, Neo4j caching
- **User Adoption**: Usability testing, intuitive GUI/graph
- **Scalability**: Chunked processing, Neo4j indexing (10,000 nodes)
- **UI/Graph Errors**: Validate uploads, test WCAG/graph rendering
- **Neo4j Learning Curve**: Use Community Edition, Claude Cypher queries, training

## 23. Acceptance Criteria
- Upload German/English PDFs; extract entries
- Import NAMUR/DIN/ASME (PDF/TBX) via GUI
- Validate entries against IEC/IATE/gold standards/Neo4j (≥90% match rate)
- Translate missing terms with manual correction
- Export glossary (CSV, Excel, JSON, TBX)
- Visualize term-standard relationships in Neo4j graph
- Version entries and relationships, auditable
- Offline operation, GDPR compliance
- UI: Dark theme (WCAG 2.1 AA), logo upload (PNG, 1MB), customizable dialog colors, progress indicators, gold standard import, graph visualization

## 24. Glossary
- GlossaryEntry: Term/definition record (SQLite)
- TBX: TermBase eXchange format
- NLP: Natural Language Processing
- IATE: EU Terminology database
- Gold Standard: NAMUR, DIN, ASME
- Neo4j: Graph database for relationships

## 25. Open Questions
- Additional languages? (Planned in enhancements)
- Deployment model? (Hybrid: local default)
- Enterprise integrations? (API hooks in future)
- Document volume? (100 docs/month, 50MB; standards 10MB)
- Glossary/graph maintenance? (Documentation teams)
- Neo4j volume? (10,000 Term nodes, 100 Standard nodes)

## 26. References
- IEC Electropedia: https://www.electropedia.org/
- IEV-Wörterbuch: https://www.electropedia.org/iev/
- IATE: https://iate.europa.eu/
- NAMUR: https://www.namur.net/en/publications/
- DIN: https://www.din.de/en
- ASME: https://www.asme.org/codes-standards
- Neo4j: https://neo4j.com/docs/
- ISO Standards: https://www.iso.org/standards.html
- DeepL: https://www.deepl.com/docs-api/
- Microsoft Translator: https://learn.microsoft.com/en-us/azure/ai-services/translator/
- GitHub: https://github.com/NCIOCPL/glossary-app, https://github.com/diegoberaldin/MetaTerm
- Claude: https://www.anthropic.com/claude
- MCP: https://modelcontextprotocol.io/
- Tools: Cursor (https://cursor.sh/), Aider (https://aider.chat/), Zed (https://zed.dev/), vis.js (https://visjs.org/), Reagraph (https://reagraph.dev/)

## 27. Revision History
- Version 1.0: Initial draft (Oct 1, 2025; User)
- Version 1.1-1.8: Added details, Claude/MCP, ASME, GUI (Oct 16, 2025; Grok)
- Version 1.9: Added Neo4j for term-standard visualization (Oct 16, 2025; Grok)
- Version 2.0: Consolidated, refined for Claude, finalized for development (Oct 16, 2025; Grok)