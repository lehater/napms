import { createTheme } from "@mui/material/styles";

export const napmsMuiTheme = createTheme({
  cssVariables: true,
  palette: {
    mode: "light",
    primary: {
      main: "#2563eb",
    },
    background: {
      default: "#f6f7f9",
      paper: "#ffffff",
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h4: {
      fontSize: "1.75rem",
      fontWeight: 650,
      letterSpacing: "-0.02em",
    },
    h6: {
      fontWeight: 650,
    },
    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: "7px 12px",
        },
        head: {
          height: 40,
          fontWeight: 650,
          whiteSpace: "nowrap",
        },
        body: {
          height: 40,
        },
      },
    },
  },
});
