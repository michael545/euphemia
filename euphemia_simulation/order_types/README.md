# Order Types for EUPHEMIA Simulation

This directory contains Python classes representing different types of orders that can be submitted to a simplified EUPHEMIA-like electricity market simulation. These classes are designed to model various bidding behaviors and order complexities found in real-world energy markets.

## Files

-   `base_order.py`: Defines the fundamental `Order` class.
-   `standard_orders.py`: Defines specific order types that inherit from the base `Order` class.

## Base Order Class (`base_order.py`)

### `Order`
The `Order` class is the foundational class for all order types in the simulation.

-   **Purpose**: To provide common attributes for all orders.
-   **Key Attributes**:
    -   `order_id`: A unique identifier for the order.
    -   `bidding_zone`: The geographical area or market zone for which the order is submitted.
    -   `side`: Indicates whether the order is a 'buy' or 'sell' order.

## Standard Order Classes (`standard_orders.py`)

This file implements various specific order types, categorized based on common market functionalities. All these classes inherit from the `Order` base class.

### 1. Aggregated Period Orders

These orders are typically submitted for individual trading periods.

#### `StepOrder(Order)`
-   **Purpose**: Represents a simple limit order, also known as a standard hourly order. It specifies a single price and quantity for a given period.
-   **Key Attributes**:
    -   `price`: The limit price for the order (€/MWh).
    -   `quantity`: The volume of the order (MWh).
    -   `period`: The specific market time unit (e.g., hour) for which the order is valid.

#### `PiecewiseLinearOrder(Order)`
-   **Purpose**: Represents an order that can be accepted gradually over a specified price range, forming a step in a supply or demand curve. Often used for bids that are not flat.
-   **Key Attributes**:
    -   `price_start`: The price at which the order begins to be accepted.
    -   `price_end`: The price at which the order is fully accepted.
    -   `quantity`: The total volume of the order (MWh) if the price is at or beyond `price_end` (for buy) or at or below `price_end` (for sell).
    -   `period`: The specific market time unit for which the order is valid.

### 2. Block Orders

Block orders are typically all-or-nothing bids that can span one or more periods and have specific acceptance conditions.

#### `BlockOrder(Order)`
-   **Purpose**: Models orders that must be accepted or rejected in their entirety (or according to a minimum acceptance ratio) and can link multiple periods with a single price.
-   **Key Attributes**:
    -   `price`: A single price limit for the entire block (€/MWh).
    -   `profile`: A dictionary mapping each period within the block to a specific volume (MWh).
    -   `min_acceptance_ratio`: The minimum proportion of the block that must be accepted (e.g., 1.0 for "fill-or-kill").
    -   `is_flexible`: Boolean indicating if the algorithm can choose the optimal period for a single-period flexible block.
    -   `exclusive_group_id`: Identifier if the block belongs to an "exclusive group" of orders where only one can be accepted.
    -   `parent_block`: Reference to a parent `BlockOrder` if part of a "linked block orders" family.
    -   `child_blocks`: List of child `BlockOrder` objects in a linked family.

### 3. Complex Orders

These are more sophisticated orders, often representing complex generation units or demand-side responses, subject to overarching conditions.

#### `ComplexOrder(Order)`
-   **Purpose**: Models orders that consist of a set of curve sub-orders (e.g., multiple `StepOrder` objects) but are treated as a single entity subject to complex conditions like minimum income or load gradients.
-   **Key Attributes**:
    -   `sub_orders`: A collection of curve sub-orders.
    -   `fixed_term`: A fixed cost or payment component in Euros, part of a Minimum Income Condition (MIC) or Maximum Payment (MP) condition.
    -   `variable_term`: A variable cost or payment component in €/MW per accepted unit, part of MIC/MP.
    -   `increase_gradient`: Maximum allowed increase in matched volume from one period to the next (MW/period).
    -   `decrease_gradient`: Maximum allowed decrease in matched volume from one period to the next (MW/period).
    -   `scheduled_stop_periods`: An array of periods during which the unit represented by the order is scheduled to be stopped.

#### `ScalableComplexOrder(ComplexOrder)`
-   **Purpose**: A variation of `ComplexOrder` with slightly different economic conditions, particularly regarding how fixed costs and minimum acceptance levels are handled.
-   **Key Attributes (in addition to `ComplexOrder` ones, with `variable_term` typically set to 0 for its primary economic condition):**
    -   `min_acceptance_powers`: A profile (dictionary) of minimum power (MW) per period required for the order to be activated.

### 4. Merit Orders

These are special, used for tie-breaking or ranking.

#### `MeritOrder(StepOrder)`
-   **Purpose**: Represents special step orders used for ranking, particularly when multiple orders are "at-the-money" (i.e., their price is equal to the clearing price).
-   **Key Attributes (in addition to `StepOrder` ones):**
    -   `merit_order_number`: A unique number assigned for ranking purposes.

### Discontinued Orders

#### `PUNOrder(MeritOrder)`
-   **Note**: USED to be relevant for the Italian market ("Prezzo Unico Nazionale"), was discontinued as JAN 2025. Was a special type of demand merit order cleared at a national PUN price.

This structure provides a flexible way to model a variety of bids and offers that come as the inputs to the EUPHEMIA algorithm.

