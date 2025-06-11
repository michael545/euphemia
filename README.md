# EUPHEMIA Study Guide

This repo is designed as a study guide for students trying to understand the EUPHEMIA algorithm.

## Table of Contents

- [Introduction to EUPHEMIA](#introduction-to-euphemia)
- [Key Concepts](#key-concepts)
- [Market Participants and roles](#market-participants-and-roles)
- [Regulatory framework](#regulatory-framework)
- [Swaps and derived Instruments](./swaps_explained.md)
- [EUPHEMIA Simulation (Python)](./euphemia_simulation/README.md)
- [Further Reading and Resources](./docs/README.md)

## Introduction to EUPHEMIA

- PCR project -- power coupling of regions (2009), SLO-IT (Day Ahead coupling in 2011)
- EUPHEMIA: Pan-European Hybrid Electricity Market Integration Algorithm
- Implemented in FEB 2014 following COSMOS/SESAME (Cross-border Optimisation of SMOS)
- Aims for transparency in the computation of prices and flows.
- Solves a complex optimization problem (usually MIQP - Mixed Integer Quadratic Programming) to achieve market coupling.

## Key Concepts/Definitions

- **Market Coupling (MC):** Eliminates the need to acquire separate transmission capacity rights for cross-border trades. Trades are determined by the MC mechanism.
- **Economic Surplus (Welfare):** The algorithm maximizes the sum of consumer surplus, producer surplus, and congestion rent across all regions.
- **Flow-Based Constraints:** Power flows induced by executed orders (net positions) must not exceed the capacity of the network.
- **PTDF (Power Transfer Distribution Factor):** Indicates how much net positions (energy exchanges) utilize the capacity of specific network elements.
- **RAM (Remaining Available Margin):** The available left capacity (in MW) on a network constraint for energy exchanges.
- **Implicit Auction:** Transmission capacity is allocated implicitly along with the energy, no need for seperate rights.

## Market Participants and Roles

- **TSOs (Transmission System Operators):** Provide transmission system constraints to the EUPHEMIA algorithm. ENTSO-E (European Network of Transmission System Operators for Electricity) has 40 TSOs from 36 countries (some countries have multiple bidding zones).
- **NEMOs (Nominated Electricity Market Operators):** Entities designated by governing bodies to operate electricity markets and interact with EUPHEMIA.
- **Market Participants Generators/Consumers:** Submit bids (asks/offers) for electricity (e.g., generators, retailers, large consumers).
    - Example: BSP SouthPool (Slovenian day-ahead market).

## Regulatory Framework

- **ACER (European Union Agency for the Cooperation of Energy Regulators):** Plays a significant oversight role.
- **National Regulatory Authorities (NRAs):** Regulate national electricity markets.
- Key EU Regulations:
    - MiFID II (Markets in Financial Instruments Directive II)
    - EMIR (European Market Infrastructure Regulation)
    - REMIT (Regulation on Wholesale Energy Market Integrity and Transparency)

## Swaps and Financial Instruments

For an explanation valuation and modelling  of power swaps and related derivatives like VPPAs, see [swaps_explained.md](./power_derivatives/swaps_explained.md).

- How much vol needs to be hedged, how much vol is pure speculation/counter trading?
- Are swaps common? Who buys options? Who writes contracts for these swaps(fixed for floating) How liquid are they?
- Who can market make options?
- PPAs (Power Purchase Agreements) / VPPAS(virtual Power  Purchase Agreements) renewables/hedging.

## EUPHEMIA Simulation (Python) Work in Progress

This repo has a super simplified Python-based simulation to show some core concepts of EUPHEMIA.
[euphemia_simulation directory](./euphemia_simulation/README.md) to see more.

## Further Reading and Resources

Useful/helpful documents, papers are in the [docs directory](./docs/README.md).

---

## Core Algorithm Principles & Notes

- **MIQP (Mixed Integer Quadratic Programming):** EUPHEMIA solves a complex optimization problem, typically an MIQP, to achieve market coupling and determine prices and flows. This is necessary to cover all requirements and provide solutions within a reasonable timeframe.

### Economic Surplus (Welfare)

The algo wants maximize the total economic surplus, calculated as:

$$
\\text{Economic Surplus (Welfare)} = \\text{Consumer Surplus} + \\text{Producer Surplus} + \\text{Congestion Rent}
$$

This surplus is a result of the executed orders in the market.

## Key Acronyms, Terms & Market Specifics

- **CWE:** Central Western Europe (a key region in European electricity markets).
- **BSP SouthPool:** The Slovenian day-ahead electricity market where participants submit bids and asks.
- **NEMO (Nominated Electricity Market Operators):** Entities designated by governing bodies to operate electricity markets and interact with EUPHEMIA. They receive transmission system constraints from TSOs as input for the algorithm.
- **PTDF (Power Transfer Distribution Factor):** A ratio indicating how much the net positions (resulting from energy exchanges) utilize the capacity of specific network elements.
## Regulators, Laws & Frameworks

- **ACER (European Union Agency for the Cooperation of Energy Regulators):** Holds a significant oversight role in the European energy markets.
- **ENTSO-E (European Network of Transmission System Operators for Electricity):** Comprises 40 Transmission System Operators (TSOs) from 36 countries across Europe. TSOs provide the transmission system constraints to EUPHEMIA.
- **ESMA (European Securities and Markets Authority):** Involved in the regulation of financial aspects of energy markets.
- **NRAs (National Regulatory Authorities):** Regulate national electricity markets.
- **SIDC (Single Intraday Coupling):** Facilitates cross-zonal intraday trading, often with auctions (e.g., 1-hour ahead).
- **Key EU Regulations:**
    - MiFID II (Markets in Financial Instruments Directive II)
    - EMIR (European Market Infrastructure Regulation)
    - REMIT (Regulation on Wholesale Energy Market Integrity and Transparency)
    These regulations are likely to continue shaping the market.

