# Vision

A locally run application for the hiring manager. Its goal is to give the hiring manager all the tools needed to run the hiring process as effectively as possible and onboard the best people available.

Basic functionalities to achieve in a semi-autonomous way:

1. Login to the internal system.
2. Talk with the user about jobs.
3. Talk with the user about interview questions.
4. Do candidate screening.

The application runs on the interviewer's own machine. Candidate data never leaves it except for the calls to the LLM provider that the features need.

## Semi-autonomous interview process

The system does the repetitive preparation work on its own, and humans make every decision that affects a candidate.

- The system proposes: questions, screening summaries, scores with reasons, follow-up suggestions.
- Humans approve, edit, or reject every proposal before it is used or stored as final.
- Nothing is sent to a candidate automatically.
- Every AI-produced output records the inputs and the model used, so a recommendation can be traced and reviewed.

Design for this boundary first. A feature that removes the human from a decision about a candidate is out of scope.
