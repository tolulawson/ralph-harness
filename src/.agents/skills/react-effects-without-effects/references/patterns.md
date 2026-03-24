# React Effects Decision Table

## Keep The Effect

- Synchronizes to external systems: network, timer, DOM/browser API, media, third-party subscriptions.
- Includes cleanup for subscriptions, listeners, and async stale-response protection.

## Replace The Effect

- Computes render-only values from existing props/state.
- Mirrors props into local state without an external synchronization need.
- Chains state across multiple Effects to model one transition.
- Notifies a parent from Effect after local state changes.

## Preferred Replacements

- Render derivation (or `useMemo` for expensive derivation).
- Event handlers for user-caused transitions.
- Keyed identity boundaries for reset semantics.
- Reducers for coordinated state transitions.
- `useSyncExternalStore` for external stores.
