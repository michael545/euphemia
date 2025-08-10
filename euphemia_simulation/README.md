# EUPHEMIA Simulation Code: Executive Summary

 A comprehensive overview of the simulation code implemented in this repository. The simulation models the EUPHEMIA algorithm, which is used for electricity market coupling across Europe. The code spans grid initialization, order handling, and optimization logic, culminating in a market-clearing solution.

## Table of Contents

- [Grid Initialization](#grid-initialization)
- [Order Types](#order-types)
- [Hourly Grid Constraints](#hourly-grid-constraints)
- [Market Clearing Optimizer](#market-clearing-optimizer)
- [Linear vs. Quadratic Modeling](#linear-vs-quadratic-modeling)

## Grid Initialization

The grid is initialized using the `Grid` class, which represents the static topology of the modeled electricity network. Components :

- **Bidding Zones**: Geographical areas where a single price is determined.
- **Interconnectors**: Transmission lines connecting bidding zones, characterized by attributes such as capacity, voltage, and coupling model (e.g., ATC or Flow-Based).

The `Grid` class also provides methods for calculating Power Transfer Distribution Factors (PTDF) and Remaining Available Margin (RAM), which are placeholders in the current implementation.

## Order Types

The simulation supports various order types, each inheriting from a base `Order` class:

- **StepOrder**: Simple limit orders with a fixed price and quantity for a single period.
- **PiecewiseLinearOrder**: Orders accepted gradually over a price range.
- **BlockOrder**: Multi-period orders with a single price and specific acceptance conditions.
- **ComplexOrder**: Sets of orders subject to overarching conditions, such as fixed and variable costs.
- **ScalableComplexOrder**: A variation of Complex Orders with additional constraints like minimum acceptance power profiles.
- **MeritOrder**: Special StepOrders used for ranking.

## Hourly Grid Constraints

The `HourlyGridConstraints` class manages time-dependent constraints for the grid:

- **Already Allocated Capacity (AAC)**: Hourly profiles for interconnectors.
- **Ramping Limits**: Maximum allowable changes in flow or net position between consecutive periods.
- **Zonal Net Position Delta Limits**: Constraints on how much a zone's net position can change hourly.

## Market Clearing Optimizer

The `MarketClearing` class implements the optimization logic using Google OR-Tools. It solves a single simple Mixed-Integer Linear Programming (MILP) problem for all 24 hourly periods. Key features include:

- **Variables**:
  - Accepted quantities for periodic orders (continuous variables).
  - Binary variables for Block and Complex orders.
  - Net positions for zones and flows on interconnectors (continuous variables).
- **Objective Function**: Maximizes social welfare by summing contributions from all order types (no Congestion rent for now).
- **Constraints**:
  - Power balance for each zone and period.
  - Flow balance for interconnectors.
  - Ramping and ATC constraints.
  - Logical constraints linking multi-period orders to their acceptance variables.

## Linear vs. Quadratic Modeling

The current model is linear because:

- The objective function is a linear combination of prices and accepted quantities.
- Constraints are linear equations or inequalities.

To make the model quadratic (MIQP):

- **Objective Function**: Introduce quadratic terms, penalizing deviations from a target flow or net position.
- **Constraints**: Add quadratic constraints, e.g., for more realistic modeling of network losses or non-linear cost functions.

---
