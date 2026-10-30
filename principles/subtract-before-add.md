# Subtract before adding

## Class

Design guidance. Hard boundaries constrain execution; design guidance requires contextual judgment.

## Applies when

Choosing a repair, refactor, or abstraction.

## Rule

Prefer deletion or a smaller existing mechanism. Add structure only when it removes a demonstrated source of complexity.

## Limits

A smaller diff must still preserve required behavior, security and verification; correctness wins over line count.
