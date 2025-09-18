---
trigger: always_on
---

## Basics
- Be careful reading multiple files to avoid context overflow.
- Always search for the proper import sources and names before adding them.
- Always search for class composition and module, and function definition before using them.
- Always keep unfinished todo items in your todo list.
- Create or open an implementation plan file for your work before you start implementing and update it as you go.

## ToDo List
- Never remove incomplete todo items.
- Add newly created todo items to the todo list.
- Rearrange todo items to keep them in a logical order if new todo items are added.

## Planning and Implementation
- The task formulation should be specific, and have all the details and constrains required to properly implement it.
- If new tasks and subtasks appear, add them to the plan file.
- Use the following marks for tasks and features:
  - `[x]` for completed tasks.
  - `✅` for completed features.
  - `[ ]` for incompleted tasks.
- Always update the plan file as you move forward with completed and new tasks.
- Decompose complex components tasks into subcomponents.
- Use the following template for the plan file:
  ```
  # Title
  Aim
  - Details

  Extended description
  - Details

  ## Guidelines
  - ...

  ## Approaches
  - ...

  ## A. Feature ...
  Estimated result
  - ...

  Extended description
  - ...
  
  Tasks
  - [x] A1. Completed Task. Simple component without subcomponents (done in one iteration or less).
    - ...
    - Result: ...
  - [ ] A2. Incompleted Task. Complex component with subcomponents.
    - ...
    - [ ] A2.1. Incompleted Subtask. Simple component.
      - ...
    - [x] A2.2. Completed Subtask. Simple component.
      - ...
      - Result: ...

  ```
