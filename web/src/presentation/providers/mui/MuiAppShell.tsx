import {
  Box,
  Button,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import type { AppShellProps } from "../../contracts";
import { muiThemeTokens as token } from "./theme-tokens.generated";

const drawerWidth = token.component.sidebarWidth;

export function MuiAppShell({
  items,
  currentPath,
  onNavigate,
  children,
}: AppShellProps) {
  const links = (
    <List aria-label="Workspaces" disablePadding>
      {items.map((item) => (
        <ListItemButton
          key={item.path}
          selected={currentPath.startsWith(item.path)}
          onClick={() => onNavigate(item.path)}
          sx={{
            borderRadius: `${token.radius.control}px`,
            mb: 0.5,
            color: token.color.navigationText,
            "&.Mui-selected": {
              bgcolor: token.color.navigationSelected,
              color: token.color.navigationText,
            },
            "&.Mui-selected:hover": {
              bgcolor: token.color.navigationSelected,
            },
          }}
        >
          <ListItemText
            primary={item.label}
            sx={{
              "& .MuiListItemText-primary": {
                fontSize: 14,
                fontWeight: 550,
              },
            }}
          />
        </ListItemButton>
      ))}
    </List>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", md: "block" },
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            bgcolor: token.color.navigationBackground,
            color: token.color.navigationText,
            borderRight: 0,
            px: 1.5,
          },
        }}
      >
        <Toolbar disableGutters sx={{ px: 1, minHeight: 72 }}>
          <Stack>
            <Typography variant="h6" color={token.color.navigationText}>
              NAPMS
            </Typography>
            <Typography variant="caption" color={token.color.navigationMutedText}>
              Policy management
            </Typography>
          </Stack>
        </Toolbar>
        <Divider sx={{ borderColor: token.color.navigationSelected, mb: 2 }} />
        <Typography
          variant="overline"
          sx={{ px: 1, mb: 0.5, color: token.color.navigationMutedText, fontWeight: 700 }}
        >
          Workspaces
        </Typography>
        {links}
      </Drawer>

      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Box
          component="nav"
          aria-label="Primary"
          sx={{
            display: { xs: "flex", md: "none" },
            gap: 0.5,
            overflowX: "auto",
            px: 2,
            py: 1,
            bgcolor: token.color.navigationBackground,
          }}
        >
          {items.map((item) => (
            <Button
              key={item.path}
              size="small"
              onClick={() => onNavigate(item.path)}
              aria-current={
                currentPath.startsWith(item.path) ? "page" : undefined
              }
              sx={{
                flex: "0 0 auto",
                color: currentPath.startsWith(item.path)
                  ? token.color.navigationText
                  : token.color.navigationMutedText,
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
        <Box
          component="main"
          sx={{
            p: {
              xs: `${token.spacing.group}px`,
              sm: `${token.component.workspacePadding}px`,
            },
            minWidth: 0,
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
