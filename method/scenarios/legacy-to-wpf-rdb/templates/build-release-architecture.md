# Build and Release Architecture

| Stage | Clean input | Command/tool/version | Output | Automated checks | Evidence retention | Owner |
|---|---|---|---|---|---|---|
| restore dependencies | | | | license/vulnerability/hash | | |
| compile | | | | warnings/analyzers | | |
| unit/contract/integration/UI | | | | | | |
| publish/package | | | | clean install | | |
| SBOM/sign | | | | signature verify | | |
| promote | | | | approval/hash equality | | |

## Branch and release train

- Protected branches:
- Required reviewers and CODEOWNERS equivalent:
- Maximum integration interval:
- Versioning and artifact identity:
- Reproducibility rule:
- Dependency cache/offline rule:
- Signing service/key custody:
- Artifact/SBOM/test evidence retention:
- Legacy-fix forward-port procedure:

