# Web UI layout

## App shell

```text
+-------------------------------------------------------------+
| Sidebar | Topbar                                            |
|         +---------------------------------------------------+
|         | Breadcrumb / PageHeader                           |
|         | Filters / Actions                                 |
|         | Main content                                      |
+---------+---------------------------------------------------+
```

## Sidebar

Responsibility: primary application navigation.

Expanded desktop width: 224-240px. Collapsed width: 64-72px. Collapse state may be stored locally because it is presentation preference, not business state.

Initial navigation:

```text
ACCESS POLICY
  Compose Connectivity
  Access Rules

POLICY VIEWS
  Effective Policy
  Normalized Policy
```

Dashboard is added only after real aggregate APIs/use cases exist. Do not add approval, user/role administration or other placeholder navigation.

## Topbar

Responsibility: global UI context/actions.

Initial content:
- current user menu;
- logout;
- optional breadcrumb below topbar.

Global search/notifications are added only with real use cases.

## Page structure

```text
PageHeader
  title
  optional description/breadcrumb
  admitted primary/secondary actions

FilterBar / Tabs when required

Content
  Table / Details / Form
```

Enterprise tables use available viewport width rather than a narrow marketing-style container.

## Drawer/dialog

Use Drawer for contextual read/light-edit detail that does not justify a separate route. Use a dedicated page for deep, multi-section or bookmarkable content. Use Dialog for confirmations and compact actions.

## Responsive behavior

- `>= 1280px`: full desktop shell;
- `768..1279px`: sidebar collapsed by default; tables may scroll horizontally;
- `< 768px`: sidebar becomes an overlay; forms/details remain functional.
