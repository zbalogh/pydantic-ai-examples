# Aster Communication Server — RAG Demo Corpus

This is a fictional, English-language internal documentation set for demonstrating retrieval-augmented generation. Aster Communication Server, its commands, API, versions, and procedures are invented; the files are not operational instructions for a real product.

## Ingestion scope

Index these six Markdown documents as the knowledge base: `overview.md`, `installation.md`, `configuration.md`, `backup-restore.md`, `troubleshooting.md`, and `release-notes.md`. Keep this README outside the indexed corpus so that the questions below test retrieval from the documentation rather than from an answer guide. Store the source filename and heading with each chunk if the loader supports metadata; answers can then cite the actual section retrieved. Split by Markdown headings when feasible, while retaining each heading with its content. If fixed-size splitting is used, choose a size that keeps the short version-specific sections together and inspect the resulting chunks before the demo.

## Suggested live-demo questions

| Question | Evidence expected from indexed documents | Test |
| --- | --- | --- |
| What is the default API port in ACS 2.3 and 2.4? | `installation.md` or `release-notes.md`: 8443 and 9443 | Version-specific exact values |
| In ACS 2.4, can I use port 8443 after upgrading? | `configuration.md` and `troubleshooting.md`: only if explicitly configured; no automatic compatibility listener | Default versus effective setting |
| Can I change retention without a restart in ACS 2.3 and 2.4? | `configuration.md`: 2.3 requires restart; 2.4 supports reload for a retention-only change within 7–365 days | Similar but different version rules |
| How do I take an online full backup in ACS 2.4? | `backup-restore.md`: consistent snapshot and WAL archiving prerequisites | Conditional procedure |
| What should I do before upgrading from 2.3 to 2.4? | `release-notes.md` and `backup-restore.md`: 2.3 full backup, maintenance, queue drain, migration, effective-port check | Multiple relevant sections |
| Why does the API appear unavailable after an upgrade to 2.4? | `troubleshooting.md`, `configuration.md`: verify port 9443 or explicit override before diagnosing further | Symptom-to-cause retrieval |
| What is the official backup retention period? | No duration is specified in the corpus | Appropriate uncertainty |
| What changed in ACS 2.5? | No ACS 2.5 documentation exists in the corpus | Refusal to invent a version |

## Answer quality checklist

A good answer identifies the relevant ACS version, distinguishes defaults from explicitly configured values, mentions prerequisites and exceptions, and cites the source file or heading if the application supports it. For the last two questions, it should say that the documentation does not provide the answer. Retrieval quality depends on the application's embedding model, splitting strategy, and search settings; these examples are test cases, not a promise that any particular configuration will retrieve every section.
