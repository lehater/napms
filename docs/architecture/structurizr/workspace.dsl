workspace "NAPMS" "C4 architecture model for the first NAPMS MVP" {
    !identifiers hierarchical

    model {
        user = person "NAPMS User" "Authors catalogue, connectivity, and access-policy data and inspects the current vendor-neutral policy."

        napms = softwareSystem "NAPMS" "Network Access Policy Management System" {
            web = container "Web Application" "Browser UI for the complete MVP authoring and policy-export journey." "Web application"

            backend = container "Backend" "Modular monolith exposing the NAPMS application API and coordinating domain modules." "Python" {
                rc = component "Resource Catalogue" "Owns Resource and current AddressSpace realization."
                acc = component "Application Communication Catalogue" "Owns ApplicationDefinition, Component, Interaction, and immutable InteractionContractRevision realization."
                ad = component "Application Deployment" "Owns ComponentDeployment realization."
                bc = component "Business Connectivity" "Owns BusinessProcess and ConnectivityNeed realization."
                ap = component "Access Policy" "Owns PolicyRule, RuleChange, and current effective policy-rule realization."
                am = component "Authority Management" "Owns effective actor/action/scope authority and protected-action admission."
                export = component "Policy Export Composition" "Read-only orchestration that materializes a complete vendor-neutral policy and table/CSV projections; owns no domain truth."
            }

            db = container "PostgreSQL" "Single physical MVP database containing module-owned persistence schemas." "PostgreSQL" "Database"
        }

        user -> napms.web "Uses"
        napms.web -> napms.backend "Uses application API" "HTTP/JSON; CSV export"
        napms.backend -> napms.db "Uses module-owned persistence" "PostgreSQL protocol"

        napms.backend.rc -> napms.db "Reads/writes Resource Catalogue-owned schema"
        napms.backend.acc -> napms.db "Reads/writes Application Communication Catalogue-owned schema"
        napms.backend.ad -> napms.db "Reads/writes Application Deployment-owned schema"
        napms.backend.bc -> napms.db "Reads/writes Business Connectivity-owned schema"
        napms.backend.ap -> napms.db "Reads/writes Access Policy-owned schema"
        napms.backend.am -> napms.db "Reads/writes Authority Management-owned schema"

        napms.backend.ad -> napms.backend.acc "Resolves Component identities through owner contract"
        napms.backend.ad -> napms.backend.rc "Resolves Resource identities through owner contract"
        napms.backend.ap -> napms.backend.ad "Validates exact deployment endpoints through owner contract"
        napms.backend.ap -> napms.backend.acc "Validates exact immutable traffic revision through owner contract"
        napms.backend.ap -> napms.backend.bc "Validates current ConnectivityNeed basis through owner contract"
        napms.backend.ap -> napms.backend.am "Requests protected-action admission"
        napms.backend.export -> napms.backend.ap "Reads effective PolicyRules"
        napms.backend.export -> napms.backend.acc "Resolves traffic revision semantics"
        napms.backend.export -> napms.backend.ad "Resolves deployment endpoints"
        napms.backend.export -> napms.backend.rc "Resolves current AddressSpace"
        napms.backend.export -> napms.backend.bc "Resolves current connectivity basis"

        mvp = deploymentEnvironment "MVP Baseline" {
            client = deploymentNode "Client" "User-side runtime for the NAPMS browser frontend." "Web browser" {
                containerInstance napms.web
            }

            applicationRuntime = deploymentNode "Backend Runtime" "Runtime hosting the single NAPMS modular-monolith backend deployment unit." "Application runtime" {
                containerInstance napms.backend
            }

            databaseRuntime = deploymentNode "Database Runtime" "Runtime hosting the single PostgreSQL deployment unit." "PostgreSQL runtime" {
                containerInstance napms.db
            }
        }
    }

    views {
        systemContext napms "SystemContext" {
            include *
            description "NAPMS first-MVP system context."
        }

        container napms "Containers" {
            include *
            description "NAPMS first-MVP runtime topology: browser frontend, modular-monolith backend, and PostgreSQL."
        }

        component napms.backend "BackendComponents" {
            include *
            description "Domain-aligned modules and policy-export composition inside the modular-monolith backend."
        }

        deployment napms mvp "MVPDeployment" {
            include *
            description "Deployment mapping for the accepted MVP baseline: browser frontend, one backend runtime, and one PostgreSQL runtime."
        }

        styles {
            element "Element" {
                shape RoundedBox
            }
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Database" {
                shape Cylinder
            }
            element "Deployment Node" {
                background #f5f5f5
                color #333333
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}
