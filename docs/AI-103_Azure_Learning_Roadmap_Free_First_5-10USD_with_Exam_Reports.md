# AI-103 Azure Learning Roadmap — Free First, $5–10 Hands-on Budget

## Your current setup

- Microsoft/Azure account
- **No Azure Free Trial**
- **No Azure for Students**
- No subscription with free credits
- Use **Pay-As-You-Go only when a real Azure lab is needed**
- Target total Azure spend: **about $5–10**

> This is a target, not a Microsoft guarantee. Azure prices vary by model, region, usage and tax.

---

## 1. AI-103 scope

Microsoft currently measures:


| Domain                                        | Weight |
| --------------------------------------------- | ------: |
| Plan and manage an Azure AI solution          | 25–30% |
| Implement generative AI and agentic solutions | 30–35% |
| Computer vision                               | 10–15% |
| Text analysis                                 | 10–15% |
| Information extraction                        | 10–15% |


Official study guide:
[https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103)

Certification:
[https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/)

You already know Python, OpenAI, RAG, agents, MCP, FastAPI and evaluation. Therefore **do not learn Azure from zero**. Learn the Microsoft implementation of concepts you already know.

---

# 2. Cost strategy

## Free first

Study these without PAYG:

- Microsoft Foundry concepts
- model selection
- agent concepts
- RAG concepts
- MCP
- evaluation
- Responsible AI
- Entra ID concepts
- RBAC concepts
- Bicep syntax
- Azure CLI syntax
- service-selection questions
- Microsoft Learn content
- exam practice

## PAYG only at hands-on gates

Use PAYG only for:

1. Foundry model deployment
2. Foundry Agent Service
3. Azure AI Search
4. Document Intelligence
5. Content Understanding
6. small Vision/Speech/Language tests
7. small Content Safety tests

---

# 3. Important cost warning

Azure **Budget alerts do NOT automatically stop consumption**. They notify you when thresholds are reached.

Official:
[https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

Cost alerts:
[https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending)

Therefore:

```text
Budget alert
    ≠
automatic spending limit
```

After each lab:

```text
Check Cost Analysis
        ↓
Check resources
        ↓
Delete unused deployment/resource
```

Use **one learning resource group**, for example:

```text
rg-ai103-lab
```

At the end, delete the resource group if you no longer need it.

---

# 4. What NOT to create

To keep the whole course around $5–10, avoid:

- GPU VMs
- AKS
- large VMs
- Provisioned Throughput
- production-scale Search
- large Content Understanding workloads
- continuous hosted agents
- large model inference
- production workloads

Use tiny datasets:

```text
5–20 documents
2–5 images
1 short audio
1 very short video
```

---

# 5. Mapping your current stack to Azure


| You already know    | Azure equivalent                           |
| ------------------- | ------------------------------------------ |
| OpenAI API          | Azure OpenAI / Foundry Models              |
| Agno Agent          | Foundry Agent Service                      |
| LangGraph           | Agent workflows / orchestration            |
| MCP                 | Foundry MCP tools                          |
| Qdrant              | Azure AI Search                            |
| Vector DB           | Azure AI Search vector index               |
| BM25 + vector       | Azure AI Search hybrid search              |
| Reranker            | Semantic ranker                            |
| RAG                 | Azure AI Search + Foundry                  |
| MinIO/S3            | Azure Blob Storage                         |
| OCR                 | Document Intelligence                      |
| VLM/multimodal      | Foundry multimodal + Content Understanding |
| Langfuse/evaluation | Foundry evaluation/tracing                 |
| OAuth/IAM           | Microsoft Entra ID                         |
| IAM permissions     | Azure RBAC                                 |
| Secrets             | Managed Identity / keyless auth            |
| Terraform           | Bicep / ARM                                |
| FastAPI             | Application layer                          |


Your main gap is therefore **Azure-specific services, configuration, identity, deployment and exam terminology**, not AI fundamentals.

---

# 6. 14-day roadmap

## DAY 0 — Setup + cost safety

Learn:

- Azure subscription
- resource group
- region
- Azure Portal
- Cost Management
- budgets
- pricing

Do not activate PAYG yet unless you are ready for the first real lab.

If PAYG is active, create a low budget and alerts.

Sources:

[https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

[https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending)

---

## DAY 1 — Microsoft Foundry

Detailed guide: [AI-103 Day 1 — Microsoft Foundry Fundamentals](AI-103_Day_1_Microsoft_Foundry_Fundamentals.md)

Learn:

- Microsoft Foundry
- Foundry resource/project
- model catalog
- Foundry Tools
- agents
- tools
- evaluations
- tracing
- governance/security

Mental model:

```text
Microsoft Foundry
├── Models
├── Agents
├── Tools
├── Knowledge
├── Evaluations
├── Tracing
└── Governance
```

**Cost: $0**

Sources:

[https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

[https://learn.microsoft.com/en-us/azure/foundry/concepts/architecture](https://learn.microsoft.com/en-us/azure/foundry/concepts/architecture)

[https://learn.microsoft.com/en-us/training/azure/ai-foundry](https://learn.microsoft.com/en-us/training/azure/ai-foundry)

---

## DAY 2 — Foundry Models / Azure OpenAI

Detailed guide: [AI-103 Day 2 — Foundry Models / Azure OpenAI](AI-103_Day_2_Foundry_Models_Azure_OpenAI.md)

Learn:

- model catalog
- model selection
- model deployment
- Standard / Global Standard / Global Provisioned
- quotas
- TPM/RPM
- pricing
- endpoint/authentication

Mental model:

```text
Azure
↓
Foundry project
↓
Model deployment
↓
Endpoint/auth
↓
Application
```

Do theory first.

Then, if needed, use PAYG for a **very small model deployment and a few API calls**.

**Target cost: **$0.50–$**2**

Sources:

[https://learn.microsoft.com/en-us/azure/ai-foundry/azure-openai-in-azure-ai-foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/azure-openai-in-azure-ai-foundry)

[https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview](https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview)

---

## DAY 3 — Foundry Agent Service

Learn:

- instructions
- conversations
- tools
- function calling
- knowledge
- memory
- multi-agent
- workflows
- approvals
- safeguards
- monitoring

Compare:

```text
Agno
Agent
├── model
├── instructions
├── tools
└── memory

Foundry
Agent
├── model
├── instructions
├── tools
├── knowledge
├── conversation
└── safeguards
```

Create one tiny agent and test:

1. basic question
2. tool call
3. structured tool
4. multi-turn conversation
5. failure case

Foundry native prompt/workflow agents have no additional agent runtime charge, but model/tool usage can cost money.

Source:
[https://azure.microsoft.com/en-us/pricing/details/foundry-agent-service/](https://azure.microsoft.com/en-us/pricing/details/foundry-agent-service/)

**Target cost: **$0.50–$**2**

---

## DAY 4 — Tools + Function Calling + MCP

Learn:

- custom tools
- function tools
- API tools
- MCP
- MCP server
- tool schema
- authentication
- permissions
- safeguards

You can build most MCP practice locally.

```text
Local MCP server
↓
Tool
↓
Foundry Agent
```

Sources:

[https://learn.microsoft.com/en-us/training/paths/develop-ai-agents-azure/](https://learn.microsoft.com/en-us/training/paths/develop-ai-agents-azure/)

[https://learn.microsoft.com/en-us/azure/foundry/agents/](https://learn.microsoft.com/en-us/azure/foundry/agents/)

**Target cost: ~$0**

---

## DAY 5 — Azure AI Search

This is one of the most important AI-103 areas.

Learn:

- Search service
- index
- fields
- analyzer
- data source
- indexer
- skillset
- embeddings
- vector search
- BM25
- hybrid search
- semantic ranker
- filters
- chunking

Architecture:

```text
Blob
 ↓
Data Source
 ↓
Indexer
 ↓
Skillset
 ↓
Index
 ↓
Vector / Keyword / Hybrid
 ↓
RAG / Agent
```

Hands-on:

- create a small Search service
- use 5–20 documents
- test keyword search
- vector search
- hybrid search
- filters
- delete the resource when finished

**Target cost: **$0–$**2**

Sources:

[https://learn.microsoft.com/en-us/azure/search/resource-training](https://learn.microsoft.com/en-us/azure/search/resource-training)

[https://learn.microsoft.com/en-us/azure/search/search-sku-tier](https://learn.microsoft.com/en-us/azure/search/search-sku-tier)

[https://learn.microsoft.com/en-us/training/modules/aaai-implement-advanced-rag-azure-ai-search/](https://learn.microsoft.com/en-us/training/modules/aaai-implement-advanced-rag-azure-ai-search/)

---

## DAY 6 — RAG + Grounding

Learn:

- ingestion
- chunking
- embeddings
- retrieval
- hybrid retrieval
- reranking
- grounding
- citations
- retrieval quality
- hallucination

Build:

```text
Documents
↓
Azure AI Search
↓
Hybrid retrieval
↓
LLM
↓
Grounded answer
```

Use only a small dataset.

**Target cost: **$0–$**1**

---

## DAY 7 — Document Intelligence

Learn:

- OCR
- Read
- Layout
- tables
- key/value
- prebuilt models
- custom extraction
- Document Intelligence vs Content Understanding

Important exam distinction:

```text
Document Intelligence
→ specialized document models
→ predictable structured extraction

Content Understanding
→ generative/multimodal
→ varying/unstructured content
→ inferred fields/reasoning
```

Hands-on:

- 2–5 PDFs/images
- OCR
- layout
- tables
- fields

**Target cost: ~**$0–$**0.50**

Source:

[https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)

[https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/choosing-right-ai-tool](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/choosing-right-ai-tool)

---

## DAY 8 — Content Understanding

Learn:

- analyzers
- documents
- images
- audio
- video
- structured output
- Markdown
- classification
- field extraction
- multimodal processing
- contextualization

Hands-on:

```text
2–5 pages
2–5 images
1 short audio
1 very short video
```

Do not process large datasets.

Current Microsoft pricing is usage-based. The pricing explainer currently describes contextualization charges and separate model/embedding charges for field extraction.

Source:
[https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/pricing-explainer](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/pricing-explainer)

**Target cost: &lt;$1**

---

## DAY 9 — Vision + Speech + Language

### Vision

- Image Analysis
- OCR
- object detection
- classification
- spatial analysis
- Custom Vision

### Speech

- speech-to-text
- text-to-speech
- speech translation

### Language

- sentiment
- NER
- PII
- summarization
- classification
- key phrases
- translation

Use free quotas/F0 where available and tiny samples.

**Target cost: ~$0**

Sources:

[https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/)

[https://learn.microsoft.com/en-us/azure/ai-services/speech-service/](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/)

[https://learn.microsoft.com/en-us/azure/ai-services/language-service/](https://learn.microsoft.com/en-us/azure/ai-services/language-service/)

---

## DAY 10 — Content Safety + Prompt Shields

Learn:

- content filtering
- harmful content
- jailbreak
- prompt injection
- indirect prompt injection
- Prompt Shields
- groundedness
- safety evaluation

Test a few cases:

```text
normal prompt
jailbreak
prompt injection
indirect injection
unsafe content
```

**Target cost: ~**$0–$**1**

Source:

[https://learn.microsoft.com/en-us/azure/ai-services/content-safety/](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/)

---

## DAY 11 — Entra ID + RBAC + Managed Identity

Learn:

- Microsoft Entra ID
- tenant
- app registration
- service principal
- managed identity
- RBAC
- role assignment
- least privilege
- keyless authentication

Mental model:

```text
User/App
↓
Entra ID
↓
Token
↓
Azure Resource
↓
RBAC
↓
Permission
```

**Target cost: $0**

Sources:

[https://learn.microsoft.com/en-us/entra/identity/](https://learn.microsoft.com/en-us/entra/identity/)

[https://learn.microsoft.com/en-us/azure/role-based-access-control/](https://learn.microsoft.com/en-us/azure/role-based-access-control/)

[https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/)

---

## DAY 12 — Evaluation + Monitoring

Learn:

- evaluation datasets
- relevance
- groundedness
- quality
- safety
- evaluators
- tracing
- monitoring
- drift
- error analysis
- provenance

Build a tiny 20-question evaluation dataset.

Compare with your Langfuse knowledge:

```text
Langfuse
→ traces + evaluations

Foundry
→ tracing + evaluations + monitoring
```

**Target cost: ~**$0–$**1**

Source:

[https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation)

---

## DAY 13 — Azure CLI + Bicep + Deployment

Learn:

- Azure CLI
- ARM
- Bicep
- parameters
- outputs
- resource groups
- deployment
- CI/CD
- deployment options

Practice:

```text
az group create
az deployment group create
```

and basic Bicep:

```text
param ...
resource ...
output ...
```

**Target cost: ~$0**

Sources:

[https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)

[https://learn.microsoft.com/en-us/cli/azure/](https://learn.microsoft.com/en-us/cli/azure/)

---

## DAY 14 — Full AI-103 Simulation

Do not learn new services.

Practice:

1. Microsoft Learn Practice Assessment
2. Exam Sandbox
3. case studies
4. Python SDK
5. JSON
6. REST
7. Azure CLI
8. Bicep
9. service selection
10. model deployment scenarios

Official certification page:

[https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/](https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-apps-and-agents-developer-associate/)

---

# 7. $5–10 budget plan


| Area                    | Target     |
| ----------------------- | ----------: |
| Foundry model inference | $1–2       |
| Agent Service           | $0.5–1.5   |
| Azure AI Search         | $0–2       |
| Document Intelligence   | $0–0.5     |
| Content Understanding   | &lt;$1     |
| Vision/Speech/Language  | ~$0        |
| Content Safety          | ~$0–1      |
| Storage                 | ~$0        |
| Entra/RBAC/Bicep/CLI    | ~$0        |
| Safety buffer           | $1–3       |
| **Target**              | **~$5–10** |


The safest strategy is to spend most of the money on **a few controlled model calls + one small Search lab**, rather than leaving services running.

---

# 8. PAYG activation checklist

Before turning on PAYG:

- [ ] Know which lab you are about to run
- [ ] Create `rg-ai103-lab`
- [ ] Know which resource(s) you will create
- [ ] Know approximate pricing
- [ ] Create cost alert/budget
- [ ] Prepare tiny test data
- [ ] Do the lab
- [ ] Check Cost Analysis
- [ ] Delete unnecessary resources

Never activate PAYG and then explore Azure randomly.

---

# 9. Things that should be hands-on at least once

```text
✓ Create Azure resource
✓ Foundry project
✓ Model deployment
✓ Call deployed model
✓ Create agent
✓ Add tool
✓ MCP
✓ Azure AI Search index
✓ Vector search
✓ Hybrid search
✓ RAG
✓ Document Intelligence
✓ Content Understanding
✓ Vision
✓ Speech
✓ Language
✓ Content Safety
✓ Entra/RBAC
✓ Managed Identity
✓ Azure CLI
✓ Bicep
✓ Cost Management
```

---

# 10. Things OpenAI API can cover before spending Azure money

You already have an OpenAI API key.

Practice locally:

```text
OpenAI API
↓
Agno / LangGraph
↓
Tool calling
↓
MCP
↓
RAG
↓
Evaluation
```

Then map:

```text
OpenAI API
→ Foundry Models

Agno
→ Foundry Agent Service

Qdrant
→ Azure AI Search

OpenAI embeddings
→ Azure embedding model

Local RAG
→ Azure AI Search + Foundry

OpenAI tool calling
→ Foundry tools

Local MCP
→ Foundry MCP tools
```

This saves Azure money while still teaching the concepts.

---

# 11. Final AI-103 mental model

```text
                     Microsoft Foundry
                            │
           ┌────────────────┼────────────────┐
           │                │                │
         Models           Agents           Tools
           │                │                │
      Azure OpenAI     Agent Service        MCP
           │                │                │
           └────────────────┼────────────────┘
                            │
                        Knowledge
                            │
                     Azure AI Search
                            │
              ┌─────────────┼─────────────┐
              │             │             │
           Vector         Hybrid       Semantic
              │             │             │
              └─────────────┼─────────────┘
                            │
                           RAG
                            │
              ┌─────────────┴─────────────┐
              │                           │
      Document Intelligence      Content Understanding
              │                           │
              └─────────────┬─────────────┘
                            │
                       Foundry Tools
                    /       |        \
                Vision    Speech    Language
                            │
                    Safety / Content
                            │
              Entra + RBAC + Managed Identity
                            │
                  CLI + Bicep + CI/CD
                            │
                  Evaluation + Monitoring
```

---

# 12. Priority for YOU

## Priority A — deep

1. Microsoft Foundry
2. Foundry Models
3. Foundry Agent Service
4. Tools + MCP
5. Azure AI Search
6. RAG
7. Document Intelligence
8. Content Understanding
9. Entra/RBAC/Managed Identity
10. Evaluation

## Priority B — enough for exam + one small lab

11. Vision
12. Speech
13. Language
14. Content Safety
15. Prompt Shields
16. CLI
17. Bicep
18. Monitoring
19. Cost/quota

## Priority C — don't deep dive

20. Generic Azure administration
21. AKS
22. GPU infrastructure
23. VM administration
24. Deep networking beyond AI-103

---

# 13. Definition of Done

You are ready when you can look at an AI system scenario and answer:

```text
Requirement
    ↓
Which Azure service?
    ↓
Which model?
    ↓
Which deployment?
    ↓
Which retrieval strategy?
    ↓
Which tool?
    ↓
Which identity?
    ↓
Which safety control?
    ↓
Which evaluation?
    ↓
How to deploy?
    ↓
How to control cost?
```

The goal is not to become an Azure Administrator.

The goal is to become:

> **An AI Engineer who can take a production AI system and implement it correctly on Microsoft Azure / Foundry.**
