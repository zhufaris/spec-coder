# Preserve observable behavior

## Class

Design guidance. Hard boundaries constrain execution; design guidance requires contextual judgment.

## Applies when

Refactoring with no authorized behavior change.

## Rule

Pin public outputs, rejection cases and observable effects before edits. Keep those pins unchanged; show structural simplification with source evidence.

## Limits

Do not manufacture behavior Red or silently fix legacy quirks. New behavior requires explicit scope and its own outcome proof.
