# Anti-patterns in Code Explanation

The ways code explanations fail, with concrete examples of each failure and what to do instead.

---

## 1. Reading the signature out loud

**Bad:** "This function `debounce(fn, delay)` takes a function `fn` and a number `delay` and returns a new function that, when called, will call `fn` after `delay` milliseconds."

That's a type signature with extra words. The reader already read the first line of the function; they do not need you to say it again.

**Better:** "Debounce is an elevator door. Every call resets a timer; the wrapped function only runs when the timer finishes without being reset. In practice: you wire it to a keystroke handler, and your search only fires 300ms after the user stops typing."

The "better" version adds the mental model (elevator door, timer that resets), the invariant (only fires if timer completes), and the realistic use case (search-on-keystroke). The reader gains something the signature didn't give them.

---

## 2. Analogies to other code

**Bad:** "It's like a stream" (talking about an iterator). "It's like a Promise" (talking about a future). "It's like a middleware" (talking about anything).

If the reader knew what a stream was, they'd understand the iterator already. Using one jargon word to explain another is not an analogy; it is a thesaurus.

**Better:** "An iterator is a vending machine. Each time you press the button, it hands you one item. When it's out, the next press lights up an 'empty' indicator instead of giving you an item."

The physical analogy works because the reader has pressed a vending machine button. You can test the model: "what happens if I press the empty button twice?" is a real question with a real answer.

---

## 3. Walkthroughs that restate the code

**Bad:**
```
Line 1: We declare a variable called `timer`.
Line 2: We return a function.
Line 3: Inside, we clear the timeout stored in `timer`.
Line 4: We set a new timeout.
```

That's the code in English. The reader can read the code in English; it's already English, mostly.

**Better:**
```
First call: `timer` is undefined; `clearTimeout(undefined)` is a safe no-op.
A new timeout is scheduled; its ID lands in `timer`.
Second call BEFORE the delay: the old timer's ID is still in `timer`.
`clearTimeout` cancels it; the scheduled callback never runs.
A fresh timeout replaces it. The OLD callback is now unreachable; garbage collector will clean up the closure next cycle.
```

The "better" version adds the state across calls, names the no-op case, and surfaces the garbage-collection detail that the code itself does not mention.

---

## 4. Generic gotchas

**Bad:** "Watch out for async behavior." "Be careful with mutation." "Don't forget error handling."

These are warnings about programming in general. They do not point at a specific trap in THIS code.

**Better:** "The `this` captured inside the setTimeout is the `this` at the moment of the LAST call, not the first. If you expected the first call's context, you'll be surprised on the second call; log `this` inside `fn` to see it change."

A gotcha should be observable (the reader can see it happen), specific to this code, and have a named cause.

---

## 5. Starting at line 1

**Bad:** Opening the explanation by walking from the top of the file, through imports, through a config block, through three helper functions, finally arriving at the function the reader actually asked about.

**Better:** Start at the function the reader asked about. If the helpers matter, bring them in as you need them: "This calls `normalize()` on line 3; `normalize()` lowercases and trims. Now line 4 makes sense." Deliver context on demand, not as a preamble.

---

## 6. Explaining the easy parts in detail

**Bad:** Spending four paragraphs on how `for` loops work, then handwaving at the critical line with "and then it recursively walks the tree."

The hard part is the hard part; that is where the reader needs you.

**Better:** Skip the `for` loop (the reader knows what a `for` loop does). Spend your paragraphs on the recursive walk: what order does it visit nodes, where does it stop, what does it mean when it returns before reaching a leaf.

The test: look at your explanation and ask "which paragraph does the reader most need?" If that paragraph is the shortest, move your weight.

---

## 7. Naming a pattern instead of explaining it

**Bad:** "This is called a monad." "This is the Observer pattern." "This uses the Visitor pattern."

Naming a pattern is not an explanation; it is a search term. If the reader knew the pattern, they would not have asked.

**Better:** Describe what the code does and the problem it solves. If the pattern name helps the reader look things up later, drop it in at the END: "what you just learned, by the way, is called the Observer pattern; now you can read other people's writing about it."

---

## 8. Seven shallow analogies

**Bad:** "A promise is like a receipt, or like a ticket, or like an IOU, or like a tracking number, or like a vending machine button."

Each analogy fires for half a sentence and does not develop. The reader gets nothing testable.

**Better:** Pick ONE analogy and push it through the whole explanation. "A Promise is a tracking number. You get it immediately when you order something. You can check its status (pending, delivered, lost). You can tell the system 'call me when this is delivered' (`.then`) or 'call me if it's lost' (`.catch`). The system remembers these instructions even if the status changes later. Multiple people can hold the same tracking number and check it independently."

The tracking number maps to every property of a Promise. It can be tested, extended, and will break at the predictable points (which you can name).

---

## 9. Hedging into meaninglessness

**Bad:** "Basically, essentially, this sort of kind of just handles the case where, generally speaking, the input might be, you know, empty or something."

Hedges stack up and the reader cannot find the claim.

**Better:** "If the input is empty, this returns `null`. That's the only case it handles specially; every other input goes through the main path."

If you're uncertain, state what you're uncertain about: "I think this returns `null` on empty input, but I'd want to check by running `fn('')` to confirm."

---

## 10. The "you should" closer

**Bad:** Ending with "so you should be careful with this" or "so make sure you understand this before using it."

That is not a closer; it is an abdication. The reader asked you for help; telling them to be careful puts the work back on them.

**Better:** End by naming what the reader can now do. "With this model, you can predict what happens when the two timers overlap: the second one wins, and the first callback is lost. You can also now safely edit the delay without worrying about breaking the cancellation logic."

The reader should leave the explanation more capable, not more cautious.
