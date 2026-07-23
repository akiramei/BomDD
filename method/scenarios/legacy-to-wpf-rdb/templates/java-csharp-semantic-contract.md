# Java → C# Semantic Compatibility Contract

各行を`preserve`、`approved-change`、`not-applicable`のいずれかで裁定する。単純な構文置換を合格にしない。

| MAP ID | Semantic area | Java/current observation | Required target behavior | .NET/C# decision | Oracle/test refs | Owner | Status |
|---|---|---|---|---|---|---|---|
| MAP-LANG-001 | null / Optional / annotations | | | nullable reference/value type | | | open |
| MAP-LANG-002 | checked/unchecked exception and cause | | | exception taxonomy/inner exception | | | open |
| MAP-LANG-003 | equality/hash/order/comparator | | | Equals/GetHashCode/IComparer | | | open |
| MAP-LANG-004 | generics, wildcards, erasure, reflection | | | .NET generics/variance/reflection | | | open |
| MAP-LANG-005 | collection order/mutability/concurrency | | | collection contract | | | open |
| MAP-LANG-006 | Stream/lazy evaluation/side effects | | | LINQ evaluation/materialization | | | open |
| MAP-LANG-007 | BigDecimal/rounding/scale | | | decimal/custom numeric | | | open |
| MAP-LANG-008 | date/time/zone/DST/locale | | | DateTime/DateTimeOffset/TimeZoneInfo | | | open |
| MAP-LANG-009 | thread/executor/future/lock/interruption | | | Task/cancellation/lock/async | | | open |
| MAP-LANG-010 | serialization/class identity/version | | | target serialization/versioning | | | open |
| MAP-LANG-011 | resource/encoding/path/line ending | | | .NET resource/UTF/path contract | | | open |
| MAP-LANG-012 | regex/string/Unicode/case | | | .NET regex/string comparison | | | open |
| MAP-LANG-013 | annotation/proxy/ServiceLoader/plugin | | | attribute/DI/reflection/plugin | | | open |
| MAP-LANG-014 | shutdown hook/finalizer/AutoCloseable | | | disposal/host shutdown | | | open |
| MAP-LANG-015 | logging/config/system properties | | | logging/configuration/options | | | open |
| MAP-LANG-016 | crypto/random/certificate/keystore | | | .NET crypto/cert store | | | open |

Completion: open 0, every preserve/change row has an oracle, and Java Technical Owner plus WPF Technical Owner approve.

