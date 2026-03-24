---
name: react-effects-without-effects
description: Review and refactor unnecessary React `useEffect` usage. Use when working on React or Next.js components and custom hooks that derive state from props or other state, mirror props into local state, trigger event-driven logic from Effects, chain Effects together, synchronize parent and child state, initialize app logic in mount Effects, or need to decide whether logic belongs in render, an event handler, `useMemo`, a keyed boundary, `useSyncExternalStore`, or a real synchronization Effect.
---

# React Effects Without Effects

## Use When

- The implementation task changes React or Next.js components, hooks, or files that include `useEffect`.

## Workflow

1. List every `useEffect` in the changed scope and ask: what external system is this synchronizing with?
2. Keep the Effect only when it synchronizes with something outside React such as network I/O, timers, browser APIs, media, or third-party subscriptions.
3. If no external system exists, remove the Effect and use a replacement pattern.
4. Confirm the component reaches the expected UI in one render pass without post-render fix-up effects.

## Replacement Patterns

### Derive During Render

- Derive computed values from props and state directly during render.
- Use `useMemo` only for expensive computations.
- Do not mirror derivable data into state.

### Handle User-Caused Logic In Events

- Put user-triggered logic in event handlers.
- Compute coordinated state transitions in one place.
- Extract shared transition helpers when several handlers need the same behavior.

### Reset By Identity

- Prefer keyed identity boundaries for full subtree resets on input changes.
- Avoid cleanup effects that only reset local state.

### Collapse Effect Chains

- Replace Effect-to-Effect state chains with event-boundary transitions or reducers.
- Keep state transitions directional and explicit.

### Use Purpose-Built Escape Hatches

- Use `useSyncExternalStore` for external mutable store subscriptions.
- Keep data-fetching Effects only when tied to external synchronization and include stale-response cleanup.

## Output Expectations

- For each changed Effect, state `keep`, `replace`, or `delete` with a one-line reason.
- Preserve behavior while reducing redundant state and post-render corrections.
- Keep diffs small and data flow easy to trace.

## Reference Map

- Read [references/patterns.md](references/patterns.md) for concise decision rules and concrete transformations.
