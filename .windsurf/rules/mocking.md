---
trigger: model_decision
description: When implementing tests
---

---
trigger: model_decision
description: When implementing tests
---

# Mocking Principle

Mocks must be used exclusively to isolate the system under test (SUT) from its external dependencies, not to simulate the entire world. The type and depth of mocking must be appropriate to the scope of the test, ensuring tests are focused, fast, and trustworthy.

## Key Implementation Guidelines

a) Isolate, Don't Simulate:
* Do: Mock the interface (e.g., a `PaymentGateway` interface), not the concrete implementation. This allows you to test the interaction contract without being coupled to the real world.

b) Mock for Different Test Types:
The strategy for mocking changes dramatically based on the test level.

| Test Type | Mocking Strategy | Goal |
| :--- | :--- | :--- |
| Unit Test | Mock all external dependencies. The SUT is a single function, class, or module. Everything else (database layers, HTTP clients, other services) should be replaced with mocks or stubs. | Verify the internal logic and outgoing commands of the SUT in perfect isolation. |
| Integration Test | Mock only cross-boundary dependencies. Use real implementations for application code (e.g., real domain services, real internal classes) but mock external infrastructure (databases, caches, message queues, third-party APIs). Use tools like testcontainers for more realistic integration. | Verify that modules integrate correctly with each other and that the contracts with external systems are obeyed. |
| End-to-End (E2E) Test | Mock nothing or mock only the most volatile/hostile externals. The entire application should be running with its real configuration. The only acceptable mocks might be for external payment gateways or email services where you can't easily control/test outcomes. | Verify the entire system works together from the user's perspective. These are slow and brittle, so use them sparingly. |

c) Focus on Interactions and States, Not Implementation:
* Interaction Testing (Using Mocks): Use a mocking framework to verify that the SUT calls the right method on a dependency with the expected arguments. This is crucial for commands (e.g., `save()`, `send()`).

d) The "Don't Mock What You Don't Own" Advisory:
* Be extremely cautious when mocking third-party libraries or SDKs you don't control. Their API can change, and your mocks will become incorrect, leading to false positives (tests pass but production code fails).
* Preferred Approach: Wrap the external library in your own thin adapter interface (e.g., `IEmailService` that wraps SendGrid's SDK). Mock your interface, not the vendor's client object. This protects your tests from vendor changes and simplifies your API.
