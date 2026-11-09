# Add Knowledge

1. Record source identity, request ID, audit file, and retrieval time.
2. Extract the complete goal, reusable methods, datasets, parameters, and code.
3. Split the complete goal into Task candidates and reusable steps into Subtask candidates. Embed scenario code and evidence in the owning Subtask's Example section.
4. Search existing assets before assigning new stable IDs to avoid duplicate capabilities.
5. Establish explicit Task-to-Subtask references and run catalog validation.
6. Run applicable embedded Examples in Earth Engine and attach execution evidence and scientific limitations.
7. Write the proposal to `knowledge/candidates/cand-*/proposed/`, validate the complete catalog with the proposal overlaid, show the diff to the user, and request approval. Publish only approved candidates.
