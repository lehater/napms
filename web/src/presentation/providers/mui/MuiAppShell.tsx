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

const drawerWidth = 232;

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
            borderRadius: 1,
            mb: 0.5,
            color: "inherit",
            "&.Mui-selected": {
              bgcolor: "rgba(255,255,255,0.14)",
              color: "common.white",
            },
            "&.Mui-selected:hover": {
              bgcolor: "rgba(255,255,255,0.18)",
            },
          }}
        >
          <ListItemText
            primary={item.label}
            primaryTypographyProps={{ fontSize: 14, fontWeight: 550 }}
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
            bgcolor: "grey.900",
            color: "grey.100",
            borderRight: 0,
            px: 1.5,
          },
        }}
      >
        <Toolbar disableGutters sx={{ px: 1, minHeight: 72 }}>
          <Stack>
            <Typography variant="h6" color="common.white">
              NAPMS
            </Typography>
            <Typography variant="caption" color="grey.400">
              Policy management
            </Typography>
          </Stack>
        </Toolbar>
        <Divider sx={{ borderColor: "rgba(255,255,255,0.12)", mb: 2 }} />
        <Typography
          variant="overline"
          sx={{ px: 1, mb: 0.5, color: "grey.500", fontWeight: 700 }}
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
            bgcolor: "grey.900",
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
                  ? "common.white"
                  : "grey.400",
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
        <Box component="main" sx={{ p: { xs: 2, sm: 3 }, minWidth: 0 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
}
