import { createTheme } from "@mui/material/styles";
import { muiThemeTokens as token } from "./theme-tokens.generated";

export const napmsMuiTheme = createTheme({
  cssVariables: true,
  palette: {
    mode: "light",
    primary: {
      main: token.color.primary,
      dark: token.color.primaryActive,
    },
    success: { main: token.color.success },
    warning: { main: token.color.warning },
    error: { main: token.color.danger },
    info: { main: token.color.info },
    background: {
      default: token.color.pageBackground,
      paper: token.color.surface,
    },
    text: {
      primary: token.color.textPrimary,
      secondary: token.color.textSecondary,
    },
    divider: token.color.border,
  },
  shape: {
    borderRadius: token.radius.surface,
  },
  typography: {
    fontFamily: token.typography.body.fontFamily,
    fontSize: token.typography.body.fontSize,
    h4: {
      fontSize: token.typography.pageTitle.fontSize,
      fontWeight: token.typography.pageTitle.fontWeight,
      lineHeight: token.typography.pageTitle.lineHeight,
      letterSpacing: token.typography.pageTitle.letterSpacing,
    },
    h6: {
      fontSize: token.typography.sectionTitle.fontSize,
      fontWeight: token.typography.sectionTitle.fontWeight,
      lineHeight: token.typography.sectionTitle.lineHeight,
    },
    body1: {
      fontSize: token.typography.body.fontSize,
      fontWeight: token.typography.body.fontWeight,
      lineHeight: token.typography.body.lineHeight,
    },
    caption: {
      fontSize: token.typography.metadata.fontSize,
      lineHeight: token.typography.metadata.lineHeight,
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
      styleOverrides: {
        root: {
          minHeight: token.component.controlHeight,
          borderRadius: token.radius.control,
          "&.Mui-focusVisible": {
            outline: `2px solid ${token.color.focus}`,
            outlineOffset: 2,
          },
          "&.MuiButton-containedPrimary:hover": {
            backgroundColor: token.color.primaryHover,
          },
          "&.MuiButton-containedPrimary:active": {
            backgroundColor: token.color.primaryActive,
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          minHeight: token.component.controlHeight,
          borderRadius: token.radius.control,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: token.radius.surface,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          padding: `${token.component.tableCellPaddingY}px ${token.component.tableCellPaddingX}px`,
        },
        head: {
          height: token.component.tableHeaderHeight,
          fontWeight: token.typography.sectionTitle.fontWeight,
          whiteSpace: "nowrap",
        },
        body: {
          height: token.component.tableRowHeight,
        },
      },
    },
  },
});
