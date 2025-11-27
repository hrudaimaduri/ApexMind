ApexMind: A Hybrid RAG × Psychological Profiling × Adaptive Coaching Agent
Technical Report — Kaggle Agents Intensive
Abstract

ApexMind is a hybrid Retrieval-Augmented Generation (RAG) system that integrates natural language retrieval, structured psychological scoring, adaptive behavioral modeling, and a longitudinal “Apex State” engine.
The agent is designed to provide personalized mindset transformation and competitive performance coaching, using RAG-grounded responses combined with dynamic user modeling.
This report describes the system architecture, retrieval pipelines, scoring methodology, adaptive state transitions, the Apex Engine, and the evaluation framework.

1. Introduction

Human performance development is not purely cognitive.
It involves feedback loops, psychological traits, consistency patterns, and strategic behavior.
ApexMind is built to model and influence these elements through:

Knowledge-grounded responses (RAG)

Psychological scoring from natural language

Long-term user memory and trait evolution

Adaptive Apex State computation

Live coaching via a modern UI

Unlike simple chatbots, ApexMind tracks user evolution over time and adjusts its coaching intensity, strategy, and mode accordingly.

2. System Overview

ApexMind consists of five major modules:

Knowledge Base

Multi-document text corpus

Pre-processed into semantic chunks

Embedding + Retrieval Layer

SentenceTransformer (all-MiniLM-L6-v2) embeddings

FAISS vector index

Metadata retrieval

LLM Reasoning Layer

Gemini 2.0 Flash model

Personality synthesis (Ego, Ayanokoji, Johan, Tokuchi)

Context-grounded and psychologically aligned coaching

Mindset Scoring Engine

Infers six psychological traits from user dialogues

EMA smoothing and long-term reinforcement

Apex Engine

Computes momentum, volatility, dominance index

Determines active “modes” (e.g., Clarity Mode, Hypergrowth Mode)

Tracks user performance over sessions

3. Knowledge Base Construction
3.1 Document Chunking

Each .txt file is split into overlapping segments (800 chars, 150 overlap).
This ensures:

Semantic coherence

High retrieval precision

Uniform embedding length

3.2 Embeddings

SentenceTransformer all-MiniLM-L6-v2 is used due to:

384-dimensional dense vectors

High performance on semantic similarity

Fast inference on CPU

3.3 Vector Index

A FAISS IndexFlatL2 index stores all chunk embeddings.
The index supports:

Fast top-k similarity search

Deterministic retrieval

Lightweight CPU-only deployment

4. Retrieval-Augmented Generation (RAG)
4.1 Query Embedding

User queries are encoded with the same transformer model.

4.2 Similarity Search

Top-k nearest chunks are retrieved via FAISS.

4.3 Context Construction

The LLM prompt includes:

System persona

Retrieved knowledge

User query

This keeps answers grounded in the curated mindset corpus.

5. LLM Reasoning Layer
5.1 Model

Gemini 2.0 Flash

High speed

Strong reasoning ability

Free-tier accessibility

5.2 Persona Synthesis

The agent blends four archetypes:

Jinpachi Ego: ruthless competitive mindset

Ayanokoji: strategic cold analysis

Johan (ethical mode): psychological insight

Tokuchi Toua: advantage-building, risk calculus

This produces direct, precise, high-performance coaching responses.

6. Mindset Scoring Engine

Each user message and agent reply is fed into a hybrid scoring model:

6.1 Traits

Discipline

Consistency

Execution

Adaptability

Ego Strength

Clarity

6.2 Scoring Mechanics

The engine extracts:

Performance signals

Confidence indicators

Emotional patterns

Strategic detail depth

Scores are then smoothed using exponential moving averages.

This creates a continuously evolving psychological profile.

7. Apex Engine

The Apex Engine introduces higher-order behavioral modeling:

7.1 Momentum

Measures positive improvement trends.

7.2 Volatility

Measures inconsistency or instability.

7.3 Dominance Index

A normalized metric representing overall competitive trajectory.

7.4 Mode Activation

Depending on score patterns, the engine activates one or more modes:

Ego Ascension

Elite Routine

Strategic Clarity

Hypergrowth

Adaptability Arc

Execution Arc
… etc.

Modes allow the system to dynamically shift coaching tone and strategy.

8. User Memory + Longitudinal Profiling

ApexMind maintains a persistent JSON profile per user ID including:

Session count

Trait EMA scores

Past interactions (CSV)

Apex state history

This allows long-term coaching across days/weeks.

9. UI Implementation

A polished Streamlit interface handles:

Chat

Live RAG context visualization

Mindset metrics

Mode activations

Apex state JSON

Persistent session timelines

The interface is intentionally transparent to help judges evaluate the agent.

10. Results

The system demonstrates:

High-quality, grounded coaching

Accurate retrieval

Stable score evolution

Distinct state transitions

Strong interpretability

Real-time visualization

Effective psychological modeling

11. Conclusion

ApexMind is a hybrid cognitive-performance agent combining:

RAG grounding

Psychological trait inference

Behavioral dynamics

Adaptive state modeling

Real-time coaching

Visual interpretability

This project demonstrates the role of hybrid architectures in advanced agent design and human augmentation.

12. Future Work

Potential extensions include:

Contrastive fine-tuning of embeddings

Reinforcement learning on mindset trajectories

Temporal graph modeling

Memory compression

Auto-habit formation protocols