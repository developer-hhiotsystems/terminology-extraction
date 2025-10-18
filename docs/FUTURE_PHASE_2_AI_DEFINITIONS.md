# Phase 2: AI-Powered Definition Generation

## Overview

Phase 2 proposes using Large Language Models (LLMs) to automatically generate high-quality, technical definitions for extracted glossary terms. This would significantly improve definition quality beyond the current context-based extraction approach.

## Current Limitation

**Phase 1 (Implemented):** Term extraction uses the complete sentence where a term appears as the definition. While this provides context, it's not always a true definition.

Example:
- **Term:** "Plant Design"
- **Current Definition:** "Term found in context (Pages 1, 3, 5): The plant design must consider modular construction principles for cost efficiency."
- **Issue:** This shows usage but doesn't define what "Plant Design" actually means.

## Proposed Solution: LLM-Based Definition Generation

### Approach

Use an LLM (e.g., GitHub Copilot, OpenAI GPT-4, or Azure OpenAI) to:

1. **Read the complete sentence** where the term appears
2. **Read surrounding context** (previous and next sentences)
3. **Generate a concise, technical definition** based on the context
4. **Format consistently** as a glossary-style entry

### Example Prompt Template

```
You are a technical glossary expert. Based on the context provided, generate a concise,
professional definition for the term "{term}".

Context:
{complete_sentence}

Additional context:
{surrounding_sentences}

Generate a definition that:
- Is 1-2 sentences maximum
- Explains what the term IS (not just how it's used)
- Uses technical but clear language
- Avoids repeating the term unnecessarily

Definition:
```

### Expected Quality Improvement

**Current (Phase 1):**
```
Term: Plant Design
Definition: Term found in context (Page 1):

The plant design must consider modular construction principles for cost efficiency.
```

**With AI (Phase 2):**
```
Term: Plant Design
Definition: The systematic process of planning and engineering the layout, systems, and infrastructure of an industrial facility, with emphasis on modular construction for operational efficiency and cost optimization.
```

## Implementation Requirements

### Prerequisites

- **LLM Access:** Requires access to an LLM API (blocked in current environment)
- **Potential Solutions:**
  - GitHub Copilot API (if approved by IT)
  - Azure OpenAI (corporate approved solution)
  - Self-hosted LLM (Llama, Mistral) on approved infrastructure
  - Offline batch processing with approved tools

### Integration Points

1. **Modify `term_extractor.py`:**
   - Add `generate_ai_definition()` method
   - Call LLM API with term + context
   - Fallback to current method if API unavailable

2. **Add configuration:**
   - Enable/disable AI definitions via config
   - API endpoint configuration
   - Cost tracking and rate limiting

3. **Update `documents.py`:**
   - Use AI definition generation when enabled
   - Log API usage and costs

### Code Skeleton

```python
# In term_extractor.py

class TermExtractor:
    def __init__(self, language: str = "en", validator = None, ai_enabled: bool = False):
        self.language = language
        self.validator = validator or create_default_validator(language)
        self.ai_enabled = ai_enabled
        self.llm_client = None

        if ai_enabled:
            # Initialize LLM client (GitHub Copilot, Azure OpenAI, etc.)
            self.llm_client = self._init_llm_client()

    def generate_definition(self, term: str, context: str,
                          complete_sentence: str = "",
                          page_numbers: List[int] = None) -> str:
        """Generate definition - uses AI if enabled, otherwise falls back to context"""

        if self.ai_enabled and self.llm_client:
            try:
                return self._generate_ai_definition(term, complete_sentence, context)
            except Exception as e:
                logger.warning(f"AI definition failed for '{term}': {e}, using fallback")
                # Fall back to context-based definition

        # Current Phase 1 approach (fallback)
        page_text = self._format_page_numbers(page_numbers)
        if complete_sentence:
            return f"Term found in context{page_text}:\n\n{complete_sentence}"
        elif context:
            return f"Term found in context{page_text}:\n\n{context[:250]}"
        else:
            return f"Technical term: {term}"

    def _generate_ai_definition(self, term: str, sentence: str, context: str) -> str:
        """Generate AI-powered definition"""

        prompt = f"""You are a technical glossary expert. Based on the context provided,
generate a concise, professional definition for the term "{term}".

Context:
{sentence}

Additional context:
{context[:500]}

Generate a definition that:
- Is 1-2 sentences maximum
- Explains what the term IS (not just how it's used)
- Uses technical but clear language
- Avoids repeating the term unnecessarily

Definition:"""

        response = self.llm_client.complete(prompt, max_tokens=150)
        definition = response.strip()

        # Add source attribution
        return f"{definition}\n\nSource: AI-generated from document context"

    def _init_llm_client(self):
        """Initialize LLM client based on configuration"""
        # GitHub Copilot, Azure OpenAI, or other approved LLM
        # Implementation depends on corporate approval
        pass
```

## Cost Estimation

### Using GitHub Copilot or Azure OpenAI

- **Estimated tokens per definition:** ~200 tokens (prompt) + 50 tokens (response) = 250 tokens
- **Current glossary size:** ~2,600 entries
- **Total tokens:** 2,600 × 250 = 650,000 tokens
- **Estimated cost (GPT-4-Turbo):** $0.01 per 1K tokens input + $0.03 per 1K tokens output
  - Input: 520,000 tokens × $0.01/1K = $5.20
  - Output: 130,000 tokens × $0.03/1K = $3.90
  - **Total: ~$9.10 for entire glossary**

### Using GPT-3.5-Turbo (Cheaper Alternative)

- **Cost:** $0.0005/1K input + $0.0015/1K output
- **Total: ~$1.10 for entire glossary**

## Quality Metrics

### Expected Improvements

| Metric | Current (Phase 1) | Expected (Phase 2) |
|--------|------------------|-------------------|
| Definition Quality | 25% excellent/good | 85-95% excellent |
| Linguistic Score | 42/100 | 85-90/100 |
| Completeness | Context-only | True definitions |
| User Satisfaction | Medium | High |

### Validation Strategy

1. Generate AI definitions for 100 sample terms
2. Human review and quality scoring
3. Compare to context-based definitions
4. Adjust prompts based on feedback
5. Roll out to full glossary if quality threshold met (>85% good)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| IT blocks LLM access | Can't implement | Document for future, use Phase 1 approach |
| High API costs | Budget concerns | Use cheaper models (GPT-3.5), batch processing |
| Generated definitions inaccurate | Poor quality | Human review workflow, confidence scoring |
| API rate limits | Slow processing | Batch processing, caching, retries |
| Data privacy concerns | Can't use cloud LLMs | Self-hosted LLM or on-prem solution |

## Timeline

### If IT Approves LLM Access

1. **Week 1:** Setup and integration
   - Configure LLM client
   - Implement generation method
   - Add configuration options

2. **Week 2:** Testing and validation
   - Generate 100 sample definitions
   - Human review and scoring
   - Adjust prompts and parameters

3. **Week 3:** Rollout
   - Process full glossary (batch mode)
   - Monitor quality and costs
   - Gather user feedback

4. **Week 4:** Refinement
   - Address quality issues
   - Optimize prompts
   - Document best practices

## Alternative: Manual Review Workflow

If LLM access is not approved, implement a **manual review workflow** instead:

1. Extract terms with Phase 1 approach (context-based)
2. Flag terms that need definition improvement
3. Provide review interface for subject matter experts
4. SMEs write proper definitions manually
5. System learns from SME definitions (future ML)

**Pros:**
- No LLM required
- High quality (human-written)
- Builds training dataset for future ML

**Cons:**
- Labor-intensive
- Slow (weeks instead of hours)
- Requires SME availability

## Conclusion

Phase 2 AI-powered definition generation would provide significant quality improvements at minimal cost (~$3-9 for full glossary). The primary blocker is corporate IT policy on LLM access.

**Recommendation:**
1. Request IT approval for GitHub Copilot or Azure OpenAI
2. Implement with fallback to Phase 1 approach
3. If blocked, document for future consideration
4. Consider manual review workflow as interim solution

**Status:** Awaiting IT approval for LLM access (GitHub Copilot mentioned as possibility)

---

**Related Documents:**
- `docs/LINGUISTIC_IMPROVEMENTS_IMPLEMENTATION.md` - Ready-to-deploy code for linguistic improvements
- `docs/LINGUISTIC_QUALITY_ASSESSMENT.md` - Detailed quality analysis
- `docs/PHASE_3.8_FINAL_SUMMARY.md` - Current system capabilities

**Last Updated:** 2025-01-18
