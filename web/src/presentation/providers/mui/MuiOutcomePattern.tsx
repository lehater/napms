import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import type { OutcomePatternProps } from "../../contracts";

export function MuiOutcomePattern({
  title,
  summary,
  tone = "info",
  details,
  provenance,
}: OutcomePatternProps) {
  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
      <Stack spacing={2}>
        <Typography variant="h6" component="h3">
          {title}
        </Typography>
        <Alert severity={tone}>{summary}</Alert>
        {details ? <Box>{details}</Box> : null}
        {provenance ? (
          <Accordion disableGutters>
            <AccordionSummary>
              <Typography sx={{ fontWeight: 650 }}>
                Provenance and history
              </Typography>
            </AccordionSummary>
            <AccordionDetails>{provenance}</AccordionDetails>
          </Accordion>
        ) : null}
      </Stack>
    </Paper>
  );
}
