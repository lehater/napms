workspace "NAPMS" "C4 architecture model for the first NAPMS MVP" {
    !identifiers hierarchical

    model {
        user = person "NAPMS User" "Uses NAPMS backend capabilities through supported clients."
        oidc = softwareSystem "OIDC Identity Provider" "External trusted issuer used for bearer-token authentication and external Group membership evidence." "External"

        napms = softwareSystem "NAPMS" "Network Access Policy Management System" {
            web = container "Web Application" "Separate browser client consuming the backend API." "Web application"

            backend = container "Backend" "Stateless modular monolith exposing the NAPMS HTTP/JSON application API." "Application" {
                org = component "Organization Structure" "Owns Organization and OrganizationalUnit identity, hierarchy, reparenting and non-destructive lifecycle."
                rc = component "Resource Catalogue" "Owns Resource identity, exactly one current OrganizationalUnit owner with ownership history, logical Endpoints, current address realization, Site/responsibility and history."
                acc = component "Application Communication Catalogue" "Owns Application, Component, independent directed Interaction and immutable InteractionRevision traffic semantics."
                ad = component "Application Deployment" "Owns immutable ComponentDeployment placement."
                bc = component "Business Connectivity" "Owns BusinessProcess, criticality attribution and participant-side ConnectivityNeed currentness/history."
                ap = component "Access Policy" "Owns AccessRequest, final permission outcomes, PolicyRule identity, evidence, justification and operational/effective state."
                am = component "Authority Management" "Evaluates authenticated actor/action/scope/time AuthorityGrants; owns no persisted assignments in the MVP."
                export = component "Policy Materialization" "Read-only shared-snapshot orchestration for scoped complete vendor-neutral policy output; owns no domain truth."
            }

            db = container "PostgreSQL" "Single physical MVP database containing module-owned persistence plus technical idempotency state." "PostgreSQL" "Database"
        }

        user -> napms.web "Uses"
        napms.web -> napms.backend "Uses application API" "HTTPS/JSON"
        napms.backend -> oidc "Fetches OIDC discovery/JWKS and validates bearer JWT" "HTTPS"
        napms.backend -> napms.db "Uses module-owned persistence" "PostgreSQL protocol"

        napms.backend.org -> napms.db "Reads/writes Organization Structure-owned schema"
        napms.backend.rc -> napms.db "Reads/writes Resource Catalogue-owned schema"
        napms.backend.acc -> napms.db "Reads/writes Application Communication Catalogue-owned schema"
        napms.backend.ad -> napms.db "Reads/writes Application Deployment-owned schema"
        napms.backend.bc -> napms.db "Reads/writes Business Connectivity-owned schema"
        napms.backend.ap -> napms.db "Reads/writes Access Policy-owned schema"
        napms.backend.am -> napms.db "Reads/writes Authority Management-owned schema"
        napms.backend -> napms.db "Reads/writes technical idempotency records"

        napms.backend.rc -> napms.backend.org "Resolves current Unit Organization membership and lifecycle"
        napms.backend.am -> napms.backend.org "Resolves Organization/Unit ancestry for scope inheritance"
        napms.backend.am -> oidc "Resolves external Group membership evidence" "OIDC/provider integration"
        napms.backend.ad -> napms.backend.acc "Resolves Component identity"
        napms.backend.ad -> napms.backend.rc "Resolves Resource identity"
        napms.backend.ap -> napms.backend.ad "Resolves exact deployments"
        napms.backend.ap -> napms.backend.acc "Validates exact immutable InteractionRevision"
        napms.backend.ap -> napms.backend.bc "Locks/resolves current Need for request/justification validation"
        napms.backend.ap -> napms.backend.rc "Resolves participating Resource AuthorityScopeRefs"
        napms.backend.ap -> napms.backend.am "Requires scoped access.request authority"
        napms.backend.export -> napms.backend.ap "Reads selected PolicyRules and provenance"
        napms.backend.export -> napms.backend.acc "Resolves traffic semantics"
        napms.backend.export -> napms.backend.ad "Resolves deployment-to-Resource facts"
        napms.backend.export -> napms.backend.rc "Resolves current organizational owners and addressed Endpoints"
        napms.backend.export -> napms.backend.org "Resolves selected Organization/Unit scope targets"
        napms.backend.export -> napms.backend.bc "Resolves Need currentness/history"
        napms.backend.export -> napms.backend.am "Requires scoped policy.export authority at evaluationAt"

        mvp = deploymentEnvironment "MVP Baseline" {
            client = deploymentNode "Client" "User-side runtime." "Web browser" {
                containerInstance napms.web
            }
            applicationRuntime = deploymentNode "Backend Runtime" "Trusted runtime behind TLS-terminating ingress." "Application runtime" {
                containerInstance napms.backend
            }
            databaseRuntime = deploymentNode "Database Runtime" "PostgreSQL runtime." "PostgreSQL runtime" {
                containerInstance napms.db
            }
        }
    }

    views {
        properties {
            "plantuml.url" "http://127.0.0.1:8081"
            "plantuml.format" "svg"
        }

        systemContext napms "SystemContext" {
            include *
            description "NAPMS first-MVP system context including external OIDC."
        }
        container napms "Containers" {
            include *
            description "Backend modular monolith, PostgreSQL and separate browser client."
        }
        component napms.backend "BackendComponents" {
            include *
            description "Domain-aligned backend modules and policy materialization composition."
        }
        deployment napms mvp "MVPDeployment" {
            include *
            description "Backend and PostgreSQL deployment baseline."
        }

        image * "DomainContextMap" {
            plantuml "generated/context-map.puml"
            title "DDD Context Map"
        }
        image * "StrategicCollaborationMap" {
            plantuml "generated/strategic-collaboration-map.puml"
            title "Strategic Collaboration Map"
        }
        image * "ResourceCatalogueDomain" {
            plantuml "generated/resource-catalogue-domain.puml"
            title "Resource Catalogue Domain Model"
        }
        image * "ResourceCatalogueProcess" {
            plantuml "generated/resource-catalogue-process.puml"
            title "Resource Catalogue Process"
        }
        image * "ApplicationCommunicationCatalogueDomain" {
            plantuml "generated/application-communication-catalogue-domain.puml"
            title "Application Communication Catalogue"
        }
        image * "ApplicationDeploymentDomain" {
            plantuml "generated/application-deployment-domain.puml"
            title "Application Deployment"
        }
        image * "BusinessConnectivityDomain" {
            plantuml "generated/business-connectivity-domain.puml"
            title "Business Connectivity"
        }
        image * "AccessPolicyDomain" {
            plantuml "generated/access-policy-domain.puml"
            title "Access Policy"
        }
        image * "FirstMVPJourney" {
            plantuml "generated/first-mvp-policy-export.puml"
            title "First MVP Policy Materialization Journey"
        }
        image * "MVPPersistenceERD" {
            plantuml "generated/mvp-persistence-erd.puml"
            title "MVP Physical Persistence ERD"
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
