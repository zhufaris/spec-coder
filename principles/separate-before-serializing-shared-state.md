# Separate before serializing shared state

## Class

Design guidance.

## Applies when

Concurrent actors share a mutable file, branch, key, or object.

## Rule

First determine whether a canonical shared target is necessary. Independent facts may each own a write target and combine at the read boundary; distinct fields in one read-modify-write file remain shared mutation. When a shared invariant is real, keep canonical ownership and use justified structural atomic or conflict coordination. Instructions to take turns are not concurrency control.

## Limits

Do not automatically split invariants, require a lock framework, or replace existing atomicity and interleaving checks. This grants no authorization.
