import { CssBaseline } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import type { ReactNode } from "react";
import { napmsMuiTheme } from "./theme";

export function MuiPresentationRoot({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider theme={napmsMuiTheme}>
      <CssBaseline enableColorScheme />
      {children}
    </ThemeProvider>
  );
}
