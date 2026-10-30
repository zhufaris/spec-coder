# Dependency direction

## Class

Design guidance.

## Applies when

A change crosses a module, framework, persistence, or context boundary.

## Rule

Keep policy independent of transport and storage. Make boundary conversion and interface ownership explicit; prove dependencies separately from behavior.

## Limits

A layer diagram is not proof. Use actual imports, types and assembly; do not add an interface for every class.
