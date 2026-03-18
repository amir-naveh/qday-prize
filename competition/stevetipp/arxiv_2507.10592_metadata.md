# arXiv Paper: 2507.10592

## Bibliographic Metadata

**Title:** Breaking a 5-Bit Elliptic Curve Key using a 133-Qubit Quantum Computer

**Author:** Steve Tippeconnic

**arXiv ID:** 2507.10592

**Submission Date:** Fri, 11 Jul 2025 19:32:38 UTC

**Primary Category:** Computer Science > Cryptography and Security (cs.CR)

**MSC Classes:** 68Q12, 81P68, 11T71

**Comments:** 32 pages, 5 figures, real hardware results from IBM Quantum, all code, circuits, and raw data are publicly available for replication

**DOI:** https://doi.org/10.48550/arXiv.2507.10592

**License:** CC BY 4.0

---

## Abstract (verbatim)

"This experiment breaks a 5-bit elliptic curve cryptographic key using a Shor-style quantum attack. Executed on IBM's 133-qubit ibm_torino with Qiskit Runtime 2.0, a 15-qubit circuit, comprised of 10 logical qubits and 5 ancilla, interferes over an order-32 elliptic curve subgroup to extract the secret scalar k from the public key relation Q = kP, without ever encoding k directly into the oracle. From 16,384 shots, the quantum interference reveals a diagonal ridge in the 32 x 32 QFT outcome space. The quantum circuit, over 67,000 layers deep, produced valid interference patterns despite extreme circuit depth, and classical post-processing revealed k = 7 in the top 100 invertible (a, b) results. All code, circuits, and raw data are publicly available for replication."

---

## Links

- Abstract page: https://arxiv.org/abs/2507.10592
- PDF: https://arxiv.org/pdf/2507.10592
