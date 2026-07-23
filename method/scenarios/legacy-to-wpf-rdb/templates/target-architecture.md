# Target Architecture

## Runtime and deployment view

| Process/service | Responsibility | Threading | Identity/privilege | Config/secret | Data/integration | Deploy/update unit | Owner |
|---|---|---|---|---|---|---|---|
| WPF desktop | | | | | | | |

## Module boundaries

| Target module | Responsibility | Allowed dependencies | Forbidden dependencies | Source workstreams | Public interfaces | Contract tests |
|---|---|---|---|---|---|---|
| MOD-REPLACE | | | | | | |

## Required decisions

- View/ViewModel/Application/Domain/Persistence responsibility.
- UI Dispatcher and background Task boundary.
- Transaction and unit-of-work boundary.
- Configuration/options validation and customer variants.
- Exception taxonomy, logging, correlation, user-facing errors.
- Process lifetime, single instance, shutdown, cancellation.
- External integration adapters and offline/network behavior.
- No generic repository/service layer without a traced consumer need.

