# Minimize reader load

## Class

Design guidance.

## Applies when

Code is difficult to trace or carries hidden or mutable state.

## Rule

Trace indirections and state a reader must hold. Prefer meaningful interface compression and locality; simplify only when it saves more reader load than it costs.

## Limits

Preserve public behavior and justified boundaries and interfaces. Do not blanket-delete wrappers or adapters.
