# Technical Roadmap - Bilingual Glossary Application
## Strategic 6-Month Infrastructure & Database Evolution Plan

**Document Version:** 1.0
**Created:** 2025-10-19
**Author:** System Architect
**Status:** DRAFT - Awaiting Approval
**Review Cycle:** Monthly

---

## Executive Summary

This roadmap balances **immediate stability needs** with **long-term scalability vision** for a bilingual (EN/DE) technical glossary extraction system. Based on comprehensive reviews from Database, System Architecture, and NLP experts, we recommend a **phased, data-quality-first approach** that defers Neo4j integration until foundational improvements are complete.

**Key Recommendation:** Fix data quality and NLP extraction first, migrate to PostgreSQL for production readiness, then integrate Neo4j for advanced relationship queries.

---

## 1. Current Architecture Assessment

### 1.1 Technology Stack (As of October 2025)

**Backend (Python 3.11+)**
- FastAPI 0.104.1 (async web framework)
- SQLAlchemy 2.0.23 (ORM)
- spaCy 3.7.2 (NLP - EN/DE models)
- pdfplumber 0.10.3 (PDF extraction)
- Neo4j 5.14.1 driver (partial implementation)

**Frontend (TypeScript/React)**
- React 18.2.0 + TypeScript 5.2.2
- Vite 5.0.8 (build tool)
- React Router 6.20.0

**Storage**
- SQLite (primary database, ~5.3MB with 2,700 terms)
- Local file system (PDF uploads)
- Neo4j (optional, infrastructure ready but not deployed)

**Lines of Code:** ~4,812 backend lines

### 1.2 Strengths (What's Working Well)

**Architecture Quality: 8.5/10**

1. **Clean Layered Design**
   - Routers (API) → Services (logic) → Models (data)
   - Clear separation of concerns
   - Proper dependency injection

2. **Data Model Excellence (9/10)**
   - Well-normalized schema (3NF)
   - Proper foreign keys and indexes
   - Bilingual support at schema level
   - Rich metadata tracking (page numbers, context excerpts)

3. **NLP Foundation (8.5/10)**
   - spaCy integration with EN/DE models
   - Robust term validation framework (8 linguistic rules)
   - **98% term extraction precision** achieved
   - Pattern-based fallback when spaCy unavailable

4. **Production-Ready Features**
   - Health check endpoints
   - CORS configuration
   - Error handling
   - API documentation (FastAPI auto-generated)

### 1.3 Bottlenecks (What's Limiting Growth)

**Critical Constraints:**

| Bottleneck | Current Impact | Urgency | Mitigation |
|------------|----------------|---------|------------|
| **SQLite Write Contention** | Limits to 5-10 concurrent users | 🔴 HIGH | Migrate to PostgreSQL |
| **26.5% Terms Have Article Prefixes** | "The Bioreactor" vs "Bioreactor" | 🔴 CRITICAL | NLP preprocessing (2-hour fix) |
| **91% Poor Definition Quality** | Context snippets, not definitions | 🔴 CRITICAL | Enhanced NLP patterns |
| **No Caching Layer** | Repeated expensive queries | 🟡 MEDIUM | Add Redis |
| **No Relationship Extraction** | Neo4j has isolated nodes | 🔴 HIGH | Dependency parsing |
| **No Authentication** | Security gap for production | 🟡 MEDIUM | JWT/OAuth2 |

**Capacity Limits (Current):**
- Documents: ~1,000 before slowdown
- Terms: ~50,000 (SQLite practical limit)
- Concurrent Users: 5-10 (write bottleneck)
- Request Throughput: ~50 req/sec (DB-limited, not API)

### 1.4 Technical Debt

**High Priority:**
1. Duplicate frontend files (App.js + App.tsx)
2. Article prefix pollution in 26.5% of terms
3. Definition extraction returns context snippets (91%)
4. No comprehensive test coverage (~30-40%)
5. No containerization (Docker)
6. No CI/CD pipeline

**Medium Priority:**
1. Files over 500 lines need splitting
2. No state management library (frontend)
3. Limited error boundaries (React)
4. No API versioning strategy

### 1.5 Scalability Limits

**Current Theoretical Capacity:**
- SQLite: 100,000 terms (practical limit ~50k for performance)
- File uploads: Limited by disk space only
- PDF processing: ~10-20 seconds per 50-page document

**With PostgreSQL Migration:**
- Terms: Millions
- Concurrent users: 100+
- Request throughput: 500+ req/sec
- Geographic distribution: Possible with read replicas

---

## 2. Database Strategy Decision

### 2.1 Expert Consensus Summary

**Database Expert Recommendation:**
> "DEFER Neo4j implementation until critical data quality and relational modeling issues are addressed first. Neo4j feasibility score: **6.5/10** (moderate benefit, not urgent)."

**System Architect Recommendation:**
> "Neo4j readiness: **75%** - Infrastructure exists but needs robust sync, relationship inference, and clean data first."

**NLP Expert Recommendation:**
> "Neo4j without relationships = expensive SQL database. Implement relationship extraction (3 weeks) BEFORE Neo4j integration for **10x better outcome**."

### 2.2 PostgreSQL Migration: When? Why? Effort?

**When:** Month 2-3 (after NLP improvements)

**Why:**
- SQLite write concurrency bottleneck
- No horizontal scaling capability
- Limited JSON query optimization
- No full-text search indexing (FTS5 is weak)
- No read replicas for high availability

**Effort Estimate:** 2 weeks
- Week 1: Setup, schema migration, data migration script
- Week 2: Testing, performance benchmarking, cutover

**Downtime:** 15-30 minutes (during low-traffic window)

**Risk:** LOW (SQLAlchemy abstracts database differences)

**Benefits:**
- Better JSON querying (JSONB vs TEXT)
- Full-text search (tsvector indexes)
- Connection pooling (pgbouncer)
- Multi-user concurrency
- Read replicas for scaling
- Industry-standard production database

**Migration Path:**
```bash
# Week 1: Preparation
1. Install PostgreSQL 15+
2. Run SQLAlchemy create_all() on PostgreSQL
3. Export SQLite → Transform JSON types → Import PostgreSQL
4. Verify data integrity (row counts, checksums)

# Week 2: Testing & Cutover
5. Run full test suite against PostgreSQL
6. Performance benchmarking
7. Blue-green deployment (keep SQLite backup)
8. Monitor production for 48 hours
```

### 2.3 Neo4j Integration: When? Prerequisites? ROI?

**When:** Month 4-5 (AFTER data quality + relationship extraction)

**Prerequisites (Critical Path):**
1. ✅ Data quality >95% (currently ~60% after article prefixes)
2. ✅ Relationship extraction implemented (5,000-8,000 edges)
3. ✅ Normalized schema (separate definitions table)
4. ✅ Relationship taxonomy defined (SYNONYM_OF, USES, PART_OF)
5. ✅ Robust sync mechanism (retry logic, monitoring)

**Effort Estimate:** 8 weeks (Phases 1-4 from System Architecture Review)
- Weeks 1-2: Foundation (connection pooling, health checks)
- Weeks 3-4: Sync infrastructure (Celery queue, retry logic)
- Weeks 5-6: Relationship intelligence (synonym detection, hierarchies)
- Weeks 7-8: Advanced features (graph visualization, analytics)

**ROI Analysis:**

| Without Neo4j | With Neo4j (Done Right) |
|---------------|------------------------|
| No relationship queries | Find synonyms, hierarchies in <100ms |
| Manual term linking | Auto-detect 70-80% of relationships |
| SQL recursive queries (slow) | Native graph traversal (fast) |
| Low user value | High user value (knowledge navigation) |

**ROI Conclusion:** Neo4j is **high value IF relationships exist**. Without relationship extraction, ROI is near zero.

### 2.4 Schema Improvements Needed First

**Priority 1: Normalize Definitions Table (Week 1)**

Current (Anti-pattern):
```python
definitions = Column(JSON)  # [{text: "...", source_doc_id: 123}]
# ❌ No FK constraint, orphan-prone
# ❌ Cannot query individual definitions
```

Recommended:
```sql
CREATE TABLE term_definitions (
    id INTEGER PRIMARY KEY,
    glossary_entry_id INTEGER NOT NULL REFERENCES glossary_entries(id),
    definition_text TEXT NOT NULL,
    source_document_id INTEGER REFERENCES uploaded_documents(id),
    is_primary BOOLEAN DEFAULT FALSE,
    extraction_confidence REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Benefits:**
- Referential integrity (FKs enforced)
- Queryable definitions
- Multiple definitions per term (proper 1:N)

**Priority 2: Add Relationship Table (Week 1)**

```sql
CREATE TABLE term_relationships (
    id INTEGER PRIMARY KEY,
    from_term_id INTEGER NOT NULL REFERENCES glossary_entries(id),
    to_term_id INTEGER NOT NULL REFERENCES glossary_entries(id),
    relationship_type VARCHAR(50) NOT NULL CHECK (
        relationship_type IN ('SYNONYM_OF', 'PART_OF', 'RELATED_TO',
                              'OPPOSITE_OF', 'ABBREVIATION_OF', 'TRANSLATES_TO')
    ),
    confidence REAL DEFAULT 1.0,
    source VARCHAR(20) DEFAULT 'manual',  -- 'manual' or 'auto-detected'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (from_term_id, to_term_id, relationship_type)
);
```

**Benefits:**
- Queryable relationships without Neo4j
- Enables SQL-based relationship queries
- Makes Neo4j **optional, not mandatory**
- Serves as data source for Neo4j sync

### 2.5 Migration Risk Assessment

**PostgreSQL Migration Risks:**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data loss during migration | LOW | CRITICAL | Automated backups, dry-run testing |
| Performance regression | LOW | MEDIUM | Benchmark before/after |
| Connection pool exhaustion | MEDIUM | MEDIUM | Configure limits, monitoring |
| Downtime exceeds 30 min | MEDIUM | MEDIUM | Blue-green deployment |

**Risk Score:** 3/10 (LOW) - SQLAlchemy abstracts most differences

**Neo4j Integration Risks:**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sync failures create inconsistency | MEDIUM | HIGH | Retry logic, batch reconciliation |
| Poor data quality in graph | HIGH | HIGH | Clean data FIRST (Priority 1) |
| Operational burden too high | MEDIUM | MEDIUM | Automate monitoring, alerts |
| Relationships don't exist | HIGH | CRITICAL | Extract relationships BEFORE Neo4j |

**Risk Score:** 6/10 (MEDIUM) - Higher complexity than PostgreSQL

---

## 3. Infrastructure Roadmap (6 Months)

### Phase 1: Foundation & Data Quality (Months 1-2)

**Goal:** Fix critical NLP issues, normalize schema, achieve production-ready data quality

#### Month 1: Critical NLP Improvements

**Week 1: Linguistic Preprocessing (CRITICAL - 5 hours work)**
- [ ] Strip article prefixes (EN: The/A/An, DE: Der/Die/Das)
  - **Impact:** Fixes 1,197 terms (26.5%) immediately
  - **Effort:** 2 hours
- [ ] OCR artifact normalization ("Tthhee" → "The")
  - **Impact:** Fixes 34 corrupted terms
  - **Effort:** 2 hours
- [ ] Whitespace normalization consistency
  - **Impact:** Fixes 682 formatting issues
  - **Effort:** 1 hour

**Expected Result:** Linguistic quality **42/100 → 70/100**

**Week 2-3: Definition Enhancement**
- [ ] Expand definitional pattern library (8 → 15+ patterns)
- [ ] Add dependency parsing for appositive detection
- [ ] Implement sentence quality scoring algorithm
- [ ] Multi-sentence definition synthesis
- [ ] Test on 100-term sample dataset

**Expected Result:** Definition quality **9/100 → 60/100**

**Week 4: Schema Normalization**
- [ ] Create `term_definitions` table (migration script)
- [ ] Create `term_relationships` table
- [ ] Migrate JSON definitions to new table
- [ ] Add foreign key constraints
- [ ] Update API to use normalized schema
- [ ] Regression testing

**Deliverable:** Clean, normalized database ready for PostgreSQL migration

#### Month 2: Relationship Extraction & PostgreSQL

**Week 5-6: Relationship Extraction (NLP)**
- [ ] Define relationship ontology (6 types minimum)
- [ ] Implement pattern-based extraction (USES, MEASURES, PART_OF)
- [ ] Implement dependency parsing extraction (SVO patterns)
- [ ] Test on sample documents
- [ ] Achieve 40-50% coverage (pattern-based)
- [ ] Achieve 70-80% coverage (dependency-based)

**Expected Result:** 5,000-8,000 relationships extracted

**Week 7-8: PostgreSQL Migration**
- [ ] Install PostgreSQL 15 (Docker or native)
- [ ] Configure connection pooling (pgbouncer)
- [ ] Run schema migration (SQLAlchemy metadata.create_all)
- [ ] Data migration script (SQLite → PostgreSQL)
- [ ] Verify data integrity (checksums, row counts)
- [ ] Performance benchmarking (before/after)
- [ ] Staging environment testing
- [ ] Production cutover (15-30 min downtime)
- [ ] 48-hour monitoring period

**Deliverable:** PostgreSQL-powered application with relationship data

**Phase 1 Milestones:**
- ✅ Linguistic quality: 70/100+
- ✅ Definition quality: 60/100+
- ✅ Relationship coverage: 70-80%
- ✅ PostgreSQL migration complete
- ✅ Normalized schema in production

---

### Phase 2: Production Readiness (Months 3-4)

**Goal:** Containerization, CI/CD, security, monitoring

#### Month 3: Infrastructure & Security

**Week 9: Containerization**
- [ ] Create Dockerfile for backend
- [ ] Create docker-compose.yml (backend + PostgreSQL + Redis)
- [ ] Multi-stage builds for optimization
- [ ] Environment-specific configs (dev/staging/prod)
- [ ] Document deployment procedure

**Week 10: CI/CD Pipeline**
- [ ] GitHub Actions workflow (or GitLab CI)
- [ ] Automated testing on commit
- [ ] Automated linting (flake8, black)
- [ ] Docker image builds
- [ ] Automated deployment to staging
- [ ] Production deployment (manual approval gate)

**Week 11: Security & Authentication**
- [ ] Implement JWT authentication
- [ ] Add role-based access control (RBAC)
- [ ] API rate limiting (per-user, per-IP)
- [ ] Secrets management (Vault or AWS Secrets Manager)
- [ ] HTTPS enforcement
- [ ] Security headers (CORS, CSP)

**Week 12: Monitoring & Observability**
- [ ] Structured logging (JSON logs)
- [ ] Prometheus metrics (request latency, error rates)
- [ ] Grafana dashboards (system health)
- [ ] Alert rules (disk space, error rates, DB connections)
- [ ] Distributed tracing (OpenTelemetry - optional)

**Deliverable:** Production-ready containerized application with security & monitoring

#### Month 4: Caching & Performance

**Week 13-14: Redis Caching Layer**
- [ ] Install Redis (Docker)
- [ ] Implement CacheService class
- [ ] Cache glossary listings (5 min TTL)
- [ ] Cache export results (15 min TTL)
- [ ] Cache Neo4j queries (10 min TTL - future)
- [ ] Cache invalidation on updates
- [ ] Performance testing (before/after)

**Expected Performance Improvement:**
- API response time: -40% average
- Database load: -60%
- Export generation: -80% (cached)

**Week 15: Frontend Optimization**
- [ ] Remove duplicate App.js (keep App.tsx only)
- [ ] Implement Zustand state management
- [ ] Add error boundaries
- [ ] React.memo for expensive components
- [ ] Virtualized lists (react-window) for 1,000+ terms
- [ ] Optimistic updates for better UX

**Week 16: Testing & Documentation**
- [ ] Add tests for term_extractor (currently missing)
- [ ] Add tests for relationship extraction
- [ ] Add integration tests for PostgreSQL
- [ ] API contract tests
- [ ] Update user documentation
- [ ] Create admin runbook

**Phase 2 Milestones:**
- ✅ Docker containers deployed
- ✅ CI/CD pipeline operational
- ✅ JWT authentication active
- ✅ Redis caching live
- ✅ Test coverage >70%
- ✅ Production monitoring dashboards

---

### Phase 3: Neo4j Integration (Months 5-6)

**Goal:** Knowledge graph with rich relationships, graph visualization

**Pre-Conditions:**
- ✅ Data quality >95% (achieved in Phase 1)
- ✅ Relationships extracted (5,000-8,000 edges)
- ✅ PostgreSQL migration complete
- ✅ Normalized schema in production
- ✅ User demand validated

#### Month 5: Neo4j Foundation & Sync

**Week 17-18: Neo4j Infrastructure**
- [ ] Install Neo4j 5.14+ (Docker or cloud)
- [ ] Configure connection pooling
- [ ] Implement health check improvements
- [ ] Add query optimization (LIMIT clauses, EXPLAIN plans)
- [ ] Create graph schema (nodes, edges, indexes)
- [ ] Define relationship types in schema

**Week 19-20: Sync Infrastructure**
- [ ] Implement Celery task queue (or FastAPI BackgroundTasks)
- [ ] Create event-driven sync architecture
- [ ] Add retry logic with exponential backoff
- [ ] Implement batch sync job (cron) for reconciliation
- [ ] Add sync status monitoring dashboard
- [ ] Test sync reliability (99%+ success target)

**Deliverable:** Reliable PostgreSQL ↔ Neo4j synchronization

#### Month 6: Relationship Intelligence & Visualization

**Week 21-22: Relationship Inference**
- [ ] Implement synonym detection (Levenshtein + definition similarity)
- [ ] Hierarchical relationship inference (compound noun analysis)
- [ ] Translation link creation (EN ↔ DE via document co-occurrence)
- [ ] Domain-based relationship suggestions
- [ ] Confidence scoring for auto-detected relationships

**Week 23-24: Advanced Features & UI**
- [ ] Graph visualization API endpoints
- [ ] Frontend graph component (D3.js or Cytoscape.js)
- [ ] Path-finding queries (shortest path between terms)
- [ ] Community detection (term clustering)
- [ ] Graph analytics (PageRank, centrality)
- [ ] User training documentation

**Phase 3 Milestones:**
- ✅ Neo4j graph live with 3,300 nodes, 5,000-8,000 edges
- ✅ Auto-sync achieving 99%+ reliability
- ✅ Relationship coverage 70-80%
- ✅ Graph visualization UI complete
- ✅ Advanced queries operational

---

## 4. Technical Decisions Needed

### 4.1 Database Choice Timeline

**Decision Point 1 (End of Month 1):** PostgreSQL Migration Approval
- **Question:** Proceed with PostgreSQL migration in Month 2?
- **Decision Criteria:**
  - Is concurrent user load exceeding 5-10 users?
  - Is dataset approaching 10,000+ terms?
  - Is production deployment planned?
- **Recommendation:** **YES** - PostgreSQL migration is essential for production

**Decision Point 2 (End of Month 2):** Neo4j Integration Approval
- **Question:** Proceed with Neo4j integration in Months 4-5?
- **Decision Criteria:**
  - Is data quality >95%? (fixed in Month 1)
  - Are relationships extracted? (completed in Month 2)
  - Is there user demand for graph features?
  - Is team ready for dual-database operations?
- **Recommendation:** Re-evaluate based on Phase 1 results

**Decision Point 3 (End of Month 4):** Scaling Strategy
- **Question:** Single PostgreSQL vs. Read Replicas vs. Microservices?
- **Decision Criteria:**
  - User base exceeding 100 concurrent users?
  - Dataset exceeding 100,000 terms?
  - Team size growing beyond 10 developers?
- **Recommendation:** Start with single PostgreSQL, add read replicas if needed

### 4.2 Deployment Infrastructure

**Option 1: Cloud-Native (Recommended for Production)**
- AWS: RDS (PostgreSQL), ECS (containers), ElastiCache (Redis)
- GCP: Cloud SQL, Cloud Run, Memorystore
- Azure: Azure Database, Container Instances, Redis Cache

**Pros:** Managed services, auto-scaling, high availability
**Cons:** Higher cost, vendor lock-in

**Option 2: Self-Hosted (VM or Bare Metal)**
- Single server: PostgreSQL + Redis + FastAPI
- Docker Compose orchestration

**Pros:** Lower cost, full control
**Cons:** Manual scaling, no managed backups

**Option 3: Hybrid**
- Database: Managed cloud (RDS)
- Compute: Self-hosted containers

**Recommendation:** Start with **Option 2** (self-hosted) for MVP, migrate to **Option 1** for production scale

### 4.3 Testing Strategy

**Current Coverage:** ~30-40% (insufficient)
**Target:** 80%+ by end of Phase 2

**Testing Pyramid:**
```
        /\
       /E2E\    5% (Cypress/Playwright)
      /─────\
     /Integr\   15% (API contract tests)
    /────────\
   /Unit Tests\ 80% (pytest)
  /────────────\
```

**Priority Tests to Add:**
1. term_extractor.py (CRITICAL - currently missing)
2. relationship extraction (NEW functionality)
3. PostgreSQL migration script (DATA INTEGRITY)
4. Neo4j sync logic (RELIABILITY)
5. API contract tests (BACKWARD COMPATIBILITY)

**Implementation Plan:**
- Month 1: Unit tests for new NLP functions
- Month 2: Integration tests for PostgreSQL
- Month 3: E2E tests for frontend flows
- Month 4: Contract tests for API versioning

### 4.4 Performance Optimization

**Current Bottlenecks:** (from Section 1.3)
1. SQLite write contention → **PostgreSQL migration**
2. No caching → **Redis (Month 4)**
3. Synchronous PDF processing → **Background tasks (already using)**
4. spaCy model loading → **Pre-load on startup (already doing)**

**Additional Optimizations (Month 4+):**
- Database query optimization (EXPLAIN ANALYZE)
- API response compression (gzip)
- CDN for static assets (frontend)
- Connection pooling tuning (pgbouncer)

**Target Performance Metrics:**
- API latency: <100ms (p95)
- PDF processing: <15 seconds per 50-page doc
- Search queries: <500ms for 10,000+ terms
- Neo4j graph queries: <200ms (2-hop traversal)

---

## 5. Decision Framework & Success Metrics

### 5.1 Go/No-Go Criteria for Each Phase

**Phase 1 (NLP + PostgreSQL):**
- ✅ Linguistic quality >70/100
- ✅ Definition quality >60/100
- ✅ Zero data loss during PostgreSQL migration
- ✅ No performance regression (must be faster)

**Phase 2 (Production Readiness):**
- ✅ Docker deployment successful
- ✅ CI/CD pipeline deploying to staging automatically
- ✅ Authentication preventing unauthorized access
- ✅ Monitoring alerts firing correctly

**Phase 3 (Neo4j):**
- ✅ Sync reliability >99%
- ✅ Relationship coverage >70%
- ✅ User testing validates graph value
- ✅ No critical bugs in production

### 5.2 Key Performance Indicators (KPIs)

**Data Quality:**
- Term precision: >95%
- Definition quality score: >60/100
- Relationship accuracy: >80%

**System Performance:**
- API uptime: 99.9%
- P95 latency: <200ms
- Database connections available: >50% capacity
- Cache hit rate: >70%

**User Metrics (Future):**
- Daily active users
- Average session duration
- Search queries per user
- Export generation frequency

### 5.3 Risk Mitigation Strategy

**For Each Major Change:**
1. Create backup (automated)
2. Test in staging environment
3. Performance benchmark (before/after)
4. Deploy during low-traffic window
5. Monitor for 48 hours
6. Rollback plan documented

**Rollback Procedures:**
- PostgreSQL migration: Revert connection string to SQLite backup
- Neo4j sync: Disable sync, continue with PostgreSQL only
- Cache layer: Remove Redis, continue without cache
- Frontend deployment: Revert to previous Docker image

---

## 6. Resource Requirements

### 6.1 Engineering Effort

**Phase 1 (Months 1-2): 320 hours**
- NLP improvements: 80 hours (2 weeks)
- Schema normalization: 40 hours (1 week)
- Relationship extraction: 120 hours (3 weeks)
- PostgreSQL migration: 80 hours (2 weeks)

**Phase 2 (Months 3-4): 320 hours**
- Containerization: 40 hours
- CI/CD: 40 hours
- Security: 80 hours (2 weeks)
- Monitoring: 40 hours
- Caching: 80 hours (2 weeks)
- Frontend: 40 hours

**Phase 3 (Months 5-6): 320 hours**
- Neo4j infrastructure: 80 hours (2 weeks)
- Sync mechanism: 80 hours (2 weeks)
- Relationship intelligence: 80 hours (2 weeks)
- Graph UI: 80 hours (2 weeks)

**Total: 960 hours (~6 person-months)**

### 6.2 Infrastructure Costs (Estimated Monthly)

**Development/Staging:**
- PostgreSQL (local Docker): $0
- Redis (local Docker): $0
- Neo4j Community (Docker): $0
- **Total: $0/month**

**Production (Cloud - AWS example):**
- RDS PostgreSQL (db.t3.medium): ~$50/month
- ElastiCache Redis (cache.t3.micro): ~$15/month
- EC2 for FastAPI (t3.medium): ~$30/month
- Neo4j Cloud (managed, optional): ~$100-200/month
- Load balancer: ~$20/month
- **Total: ~$115-315/month** (depending on Neo4j)

**Alternative (Self-Hosted):**
- Single VPS (8GB RAM, 4 vCPU): ~$40-80/month
- Backup storage: ~$10/month
- **Total: ~$50-90/month**

### 6.3 Team Requirements

**Minimum Viable Team:**
- 1x Backend Engineer (Python, FastAPI, SQLAlchemy)
- 1x NLP Engineer (spaCy, linguistics)
- 0.5x DevOps (Docker, CI/CD) - can be shared
- 0.5x Frontend (React, TypeScript) - can be shared

**Ideal Team (Phase 3):**
- Add: 1x Database Specialist (PostgreSQL + Neo4j)
- Add: 1x QA Engineer (testing, automation)

---

## 7. Alternative Scenarios

### 7.1 Fast-Track Scenario (3 Months)

**If timeline is critical:**
- Month 1: NLP fixes + PostgreSQL migration (combined)
- Month 2: Production readiness (Docker, CI/CD, security)
- Month 3: Skip Neo4j, focus on stability

**Trade-offs:**
- No Neo4j integration
- Minimal relationship extraction
- Less testing coverage
- Higher technical debt

**When to Use:** MVP launch with tight deadline

### 7.2 Conservative Scenario (9-12 Months)

**If quality is paramount:**
- Months 1-2: NLP improvements (Phase 1 as planned)
- Months 3-4: Extensive testing, user feedback
- Months 5-6: PostgreSQL migration with zero risk
- Months 7-8: Production readiness
- Months 9-10: Neo4j integration
- Months 11-12: Advanced features, optimization

**Trade-offs:**
- Slower delivery
- Higher engineering cost
- More thorough validation

**When to Use:** Enterprise deployment, compliance requirements

### 7.3 No-Neo4j Scenario (Simpler Stack)

**If graph features are not needed:**
- Month 1-2: NLP improvements + PostgreSQL migration
- Month 3-4: Production readiness
- Month 5-6: Advanced search, analytics (SQL-based)

**Use PostgreSQL + AGE (Graph Extension) instead:**
- Single database (no sync complexity)
- SQL + Cypher queries in PostgreSQL
- Lower operational overhead

**Trade-offs:**
- Slower graph queries than native Neo4j
- AGE is less mature than Neo4j

**When to Use:** Budget constraints, small team, limited graph use cases

---

## 8. Recommended Path Forward

### 8.1 Architect's Final Recommendation

**Adopt the Standard 6-Month Roadmap:**
- Months 1-2: Data Quality + PostgreSQL (Phase 1)
- Months 3-4: Production Readiness (Phase 2)
- Months 5-6: Neo4j Integration (Phase 3)

**Rationale:**
1. **Data quality first** - Without clean data, Neo4j is worthless
2. **PostgreSQL is essential** - SQLite cannot support production load
3. **Relationship extraction is critical** - Neo4j needs rich edges, not just nodes
4. **Phased approach reduces risk** - Each phase has clear deliverables and rollback plans

### 8.2 Immediate Next Steps (Week 1)

**Priority 1 (Do Immediately - 5 hours):**
1. Implement article stripping (2 hours)
2. Add OCR normalization (2 hours)
3. Fix whitespace issues (1 hour)

**Impact:** Linguistic quality jumps from 42/100 to 70/100

**Priority 2 (Week 1 - 2 days):**
1. Create schema migration script (term_definitions table)
2. Create term_relationships table
3. Document relationship taxonomy (6 types)

**Priority 3 (Week 1 - 1 day):**
1. Approve roadmap with stakeholders
2. Allocate engineering resources
3. Set up project tracking (JIRA, GitHub Projects)

### 8.3 Stakeholder Approval Checklist

- [ ] Database migration timeline approved
- [ ] Neo4j integration deferred to Month 5 (approved)
- [ ] Engineering resource allocation confirmed
- [ ] Infrastructure budget approved
- [ ] Success metrics agreed upon
- [ ] Rollback procedures documented

---

## 9. Conclusion

This roadmap balances **pragmatic short-term fixes** with **strategic long-term vision**. By prioritizing data quality and relationship extraction before Neo4j, we maximize ROI and minimize technical debt.

**Key Takeaways:**
1. Fix the **26.5% article prefix problem** first (2-hour fix, massive impact)
2. **PostgreSQL migration is non-negotiable** for production
3. **Neo4j is valuable only with relationships** - extract them first
4. **Phased approach** allows course correction based on results

**Expected Outcomes (6 Months):**
- Data quality: 95%+
- System scalability: 100x improvement (100+ concurrent users)
- Knowledge graph: 3,300 nodes, 5,000-8,000 edges
- Production-ready: Docker, CI/CD, monitoring, security
- User value: High (professional definitions, relationship navigation)

---

**Document Status:** DRAFT - Awaiting Approval
**Next Review:** End of Month 1 (after Phase 1 Week 4)
**Owner:** System Architect
**Last Updated:** 2025-10-19
